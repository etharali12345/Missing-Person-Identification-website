from __future__ import annotations
import logging
import os
import uuid
from typing import Optional, Tuple
import MySQLdb.cursors
import cv2
import faiss
import numpy as np
import onnxruntime as ort

logger = logging.getLogger(__name__)


BASE_DIR   = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATIC_DIR = os.path.join(BASE_DIR, "static")

MISSING_IMG_DIR = os.path.join(STATIC_DIR, "uploads", "missing")
FOUND_IMG_DIR   = os.path.join(STATIC_DIR, "uploads", "found")

MISSING_FAISS_PATH = os.environ.get(
    "MISSING_FAISS_PATH", os.path.join(BASE_DIR, "faiss_indexes", "missing_persons.index")
)
FOUND_FAISS_PATH = os.environ.get(
    "FOUND_FAISS_PATH", os.path.join(BASE_DIR, "faiss_indexes", "found_persons.index")
)

ATTRIB_MODEL_PATH = os.environ.get(
    "ATTRIB_MODEL_PATH", os.path.join(BASE_DIR, "models", "model.onnx")
)

FACE_EMBEDDING_DIM = 512

# ============================================================================

def _ensure_dirs() -> None:
    for d in (
        MISSING_IMG_DIR,
        FOUND_IMG_DIR,
        os.path.dirname(MISSING_FAISS_PATH),
        os.path.dirname(FOUND_FAISS_PATH),
    ):
        os.makedirs(d, exist_ok=True)


# ============================================================================

_faiss_cache: dict[str, faiss.Index] = {}


def _faiss_path(category: str) -> str:
    if category == "missing":
        return MISSING_FAISS_PATH
    if category == "found":
        return FOUND_FAISS_PATH
    raise ValueError(f"Unknown FAISS category: {category!r}")


def load_faiss_index(category: str) -> faiss.Index:
    if category in _faiss_cache:
        return _faiss_cache[category]

    path = _faiss_path(category)
    if os.path.exists(path):
        index = faiss.read_index(path)
        logger.info("[FAISS] Loaded %s index from disk (%d vectors)", category, index.ntotal)
    else:
        _ensure_dirs()
        flat  = faiss.IndexFlatIP(FACE_EMBEDDING_DIM)
        index = faiss.IndexIDMap2(flat)           
        logger.info("[FAISS] Created new %s index", category)

    _faiss_cache[category] = index
    return index


def _save_faiss_index(index: faiss.Index, category: str) -> None:
    _ensure_dirs()
    faiss.write_index(index, _faiss_path(category))
    _faiss_cache[category] = index


def add_embedding_to_index(embedding: np.ndarray, category: str, faiss_id: int) -> int:
    index = load_faiss_index(category)
    vec = embedding.astype(np.float32).reshape(1, -1)
    ids = np.array([faiss_id], dtype=np.int64)
    index.add_with_ids(vec, ids)
    _save_faiss_index(index, category)
    logger.debug("[FAISS] Added to '%s' index → faiss_id=%d", category, faiss_id)
    return faiss_id


def delete_embedding_from_index(faiss_id: int, category: str) -> None:
    try:
        index  = load_faiss_index(category)
        id_sel = faiss.IDSelectorBatch(np.array([faiss_id], dtype=np.int64))
        removed = index.remove_ids(id_sel)
        _save_faiss_index(index, category)
        logger.debug("[FAISS] Removed faiss_id=%d from '%s' index (removed=%d)", faiss_id, category, removed)
    except Exception:
        logger.exception("[FAISS] Failed to delete faiss_id=%d from '%s' index", faiss_id, category)


def search_faiss_index(
    embedding: np.ndarray, category: str, top_k: int = 1
) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    index = load_faiss_index(category)
    if index.ntotal == 0:
        logger.warning("[FAISS] '%s' index is empty — skipping search", category)
        return None, None

    vec = embedding.astype(np.float32).reshape(1, -1)
    distances, indices = index.search(vec, top_k)
    logger.debug(
        "[FAISS] Search '%s': similarity=%.4f idx=%d",
        category, distances[0][0], indices[0][0],
    )
    return distances, indices


# ============================================================================

_detector_app = None

def _get_detector_app():
    global _detector_app
    if _detector_app is None:
        from insightface.app import FaceAnalysis
        _detector_app = FaceAnalysis(
            name="buffalo_l",
            allowed_modules=["detection"],
            providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
        )
        _detector_app.prepare(ctx_id=0, det_size=(320, 320))
        logger.info("[InsightFace] Detection-only model loaded")
    return _detector_app


_attrib_session = None

def _get_attrib_session() -> ort.InferenceSession:
    global _attrib_session
    if _attrib_session is None:
        _attrib_session = ort.InferenceSession(
            ATTRIB_MODEL_PATH,
            providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
        )
        logger.info("[AttribNet] ONNX session loaded from %s", ATTRIB_MODEL_PATH)
    return _attrib_session


def _align_face_crop(img: np.ndarray, face) -> np.ndarray:
    kps = face.kps
    h, w = img.shape[:2]

    x1, y1, x2, y2 = face.bbox.astype(int)
    pad = int(max(x2 - x1, y2 - y1) * 0.4)
    x1c = max(0, x1 - pad)
    y1c = max(0, y1 - pad)
    x2c = min(w, x2 + pad)
    y2c = min(h, y2 + pad)
    crop = img[y1c:y2c, x1c:x2c]

    left_eye  = kps[0] - np.array([x1c, y1c])
    right_eye = kps[1] - np.array([x1c, y1c])

    dx = right_eye[0] - left_eye[0]
    dy = right_eye[1] - left_eye[1]
    angle = np.degrees(np.arctan2(dy, dx))

    eye_center = (
        float((left_eye[0] + right_eye[0]) / 2),
        float((left_eye[1] + right_eye[1]) / 2),
    )
    ch, cw = crop.shape[:2]
    M = cv2.getRotationMatrix2D(eye_center, angle, scale=1.0)
    aligned_crop = cv2.warpAffine(crop, M, (cw, ch), flags=cv2.INTER_LINEAR)

    return aligned_crop


def _preprocess_attrib(face_crop: np.ndarray) -> np.ndarray:
    face = cv2.resize(face_crop, (128, 128))
    face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
    face = face.astype(np.uint8)
    face = np.transpose(face, (2, 0, 1))
    return face[None, ...]


def _run_attrib_check(face_crop: np.ndarray, threshold: int = 250) -> Tuple[bool, str]:
    session = _get_attrib_session()
    x = _preprocess_attrib(face_crop)
    pred = session.run(["probability"], {"image": x})[0][0]

    left_eye_score   = int(pred[0])
    right_eye_score  = int(pred[1])
    mask_score       = int(pred[3])
    sunglasses_score = int(pred[4])

    logger.debug(
        "[AttribNet] left_eye=%d right_eye=%d mask=%d sunglasses=%d",
        left_eye_score, right_eye_score, mask_score, sunglasses_score,
    )

    if mask_score > threshold:
        return True, "تظهر الصورة شخص يرتدي كمامة أو ما يشابهها، يرجى رفع صورة تظهر ملامح الوجه بوضوح"

    if sunglasses_score > threshold:
        return True, "تظهر الصورة شخص يرتدي نظارة شمسية أو ما يشابهها، يرجى رفع صورة تظهر العينين بوضوح"

    return False, "ok"


def enhance_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray)

    target = 120.0
    ratio = target / (mean_brightness + 1e-5)

    alpha = float(np.clip(ratio, 0.9, 1.1))
    beta = 10 if mean_brightness < 120 else 0  # only add brightness if image is dark

    img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
    return img


_insight_app = None


def _get_insight_app():
    global _insight_app
    if _insight_app is None:
        from insightface.app import FaceAnalysis
        _insight_app = FaceAnalysis(
            name="buffalo_l",
            providers=["CUDAExecutionProvider", "CPUExecutionProvider"],
        )
        _insight_app.prepare(ctx_id=0, det_size=(640, 640))
        logger.info("[InsightFace] Full recognition model loaded")
    return _insight_app


def extract_embedding(image_path: str) -> Tuple[Optional[np.ndarray], Optional[str]]:
    full_path = os.path.join(BASE_DIR, image_path) if not os.path.isabs(image_path) else image_path
    img = cv2.imread(full_path)
    img = enhance_image(img)
    if img is None:
        logger.warning("[PIPELINE] Cannot read image: %s", full_path)
        return None, "تعذّر قراءة الصورة المرفوعة."

    detector = _get_detector_app()
    faces = detector.get(img)

    if len(faces) == 0:
        logger.info("[PIPELINE] No face detected in %s", full_path)
        return None, "لم يتم اكتشاف أي وجه في الصورة، يرجى رفع صورة أوضح."

    if len(faces) > 1:
        logger.info("[PIPELINE] Multiple faces (%d) in %s", len(faces), full_path)
        return None, "تم اكتشاف أكثر من وجه في الصورة، يرجى رفع صورة تحتوي على وجه واحد فقط."

    face = faces[0]
    h, w = img.shape[:2]

    crop = _align_face_crop(img, face)
    if crop is None or crop.size == 0:
        return None, "تعذر اقتصاص الوجه المكتشف، يرجى تجربة صورة مختلفة."

    rejected, reason = _run_attrib_check(crop)
    if rejected:
        logger.info("[PIPELINE] Attribute rejection: %s", reason)
        return None, reason

    app = _get_insight_app()
    faces_full = app.get(img)

    if not faces_full:
        pad = int(max(h, w) * 0.3)
        img_padded = cv2.copyMakeBorder(
            img, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0)
        )
        faces_full = app.get(img_padded)

    if not faces_full:
        return None, "تعذر التعرف على الوجه، يرجى رفع صورة أوضح"

    best_face = max(faces_full, key=lambda f: f.det_score)
    embedding = best_face.normed_embedding.astype(np.float32)
    logger.info("[PIPELINE] Embedding extracted successfully from %s", full_path)
    return embedding, None


# ============================================================================

def save_image(file_storage, category: str) -> str:
    if not hasattr(file_storage, "save"):
        raise ValueError("file_storage must be a Werkzeug FileStorage object")

    _ensure_dirs()
    dest_dir = MISSING_IMG_DIR if category == "missing" else FOUND_IMG_DIR

    ext = os.path.splitext(file_storage.filename or "")[1].lower() or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    abs_path = os.path.join(dest_dir, filename)

    file_storage.save(abs_path)

    if not os.path.exists(abs_path):
        raise IOError(f"Image was not saved to {abs_path}")

    rel_path = f"static/uploads/{category}/{filename}"
    logger.debug("[SAVE] Image saved → %s", rel_path)
    return rel_path


def sanitize_value(value, expected_type: str = "str"):
    if hasattr(value, "read") or hasattr(value, "filename"):
        raise ValueError("FileStorage object passed to sanitize_value — use image path instead")

    if value is None or str(value).strip() == "":
        return None

    if expected_type == "int":
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    if expected_type == "phone":
        cleaned = str(value).strip()
        return cleaned if cleaned else None

    return str(value).strip() or None


def get_missing_person_by_faiss_id(mysql, faiss_id: int) -> Optional[dict]:
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(
            """
            SELECT missing_id, full_name, age, gender,
                   last_seen_date, last_seen_location, image_path,
                   phone_number1, phone_number2, faiss_id
            FROM   missing_persons
            WHERE  faiss_id = %s
            LIMIT  1
            """,
            (faiss_id,),
        )
        row = cur.fetchone()
        cur.close()
        return row
    except Exception:
        logger.exception("[DB] get_missing_person_by_faiss_id failed for faiss_id=%s", faiss_id)
        return None


def get_found_person_by_faiss_id(mysql, faiss_id: int) -> Optional[dict]:
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(
            """
            SELECT
                fp.found_id, fp.full_name, fp.approximate_age, fp.gender, fp.health_status,
                fp.found_date, fp.found_location, fp.image_path, fp.phone_number1, fp.phone_number2,
                fp.faiss_id,
                COALESCE(
                    a.authority_name,
                    CONCAT(u.first_name, ' ', u.last_name)
                ) AS authority_name,
                CASE
                    WHEN fp.authority_id IS NOT NULL THEN 'authority'
                    WHEN fp.uploaded_by_admin_id IS NOT NULL THEN 'admin'
                END AS uploaded_by_type
            FROM found_persons fp
            LEFT JOIN authority a
                ON fp.authority_id = a.authority_id
            LEFT JOIN users u
                ON fp.uploaded_by_admin_id = u.user_id
            WHERE fp.faiss_id = %s
            LIMIT 1
            """,
            (faiss_id,),
        )
        row = cur.fetchone()
        cur.close()
        return row
    except Exception:
        logger.exception("[DB] get_found_person_by_faiss_id failed for faiss_id=%s", faiss_id)
        return None


def delete_image_safe(image_path: str):
    try:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
    except Exception:
        logger.warning("Could not delete orphaned image: %s", image_path)