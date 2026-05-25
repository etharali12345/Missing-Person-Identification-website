from __future__ import annotations
import logging
import os
import traceback
import uuid
from typing import Optional, Tuple, Union
import MySQLdb.cursors
import cv2
import faiss
import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------

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

FACE_EMBEDDING_DIM = 512
BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")

# ---------------------------------------------------------------------------
# Directory bootstrap
# ---------------------------------------------------------------------------

def _ensure_dirs() -> None:
    for d in (
        MISSING_IMG_DIR,
        FOUND_IMG_DIR,
        os.path.dirname(MISSING_FAISS_PATH),
        os.path.dirname(FOUND_FAISS_PATH),
    ):
        os.makedirs(d, exist_ok=True)


# ---------------------------------------------------------------------------
# FAISS — in-memory cache
# ---------------------------------------------------------------------------

_faiss_cache: dict[str, faiss.Index] = {}


def _faiss_path(category: str) -> str:
    if category == "missing":
        return MISSING_FAISS_PATH
    if category == "found":
        return FOUND_FAISS_PATH
    raise ValueError(f"Unknown FAISS category: {category!r}")


def load_faiss_index(category: str) -> faiss.Index:
    """Return cached index, loading from disk or creating fresh if needed."""
    if category in _faiss_cache:
        return _faiss_cache[category]

    path = _faiss_path(category)
    if os.path.exists(path):
        index = faiss.read_index(path)
        logger.info("[FAISS] Loaded %s index from disk (%d vectors)", category, index.ntotal)
    else:
        _ensure_dirs()
        index = faiss.IndexFlatIP(FACE_EMBEDDING_DIM)
        logger.info("[FAISS] Created new %s index", category)

    _faiss_cache[category] = index
    return index


def _save_faiss_index(index: faiss.Index, category: str) -> None:
    _ensure_dirs()
    faiss.write_index(index, _faiss_path(category))
    _faiss_cache[category] = index


def add_embedding_to_index(embedding: np.ndarray, category: str) -> int:
    index = load_faiss_index(category)
    vec   = embedding.astype(np.float32).reshape(1, -1)
    index.add(vec)
    faiss_id = index.ntotal - 1
    _save_faiss_index(index, category)
    logger.debug("[FAISS] Added to '%s' index → faiss_id=%d", category, faiss_id)
    return faiss_id


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


# ---------------------------------------------------------------------------
# InsightFace singleton
# ---------------------------------------------------------------------------

_insight_app = None


def _get_insight_app():
    global _insight_app
    if _insight_app is None:
        from insightface.app import FaceAnalysis
        _insight_app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
        _insight_app.prepare(ctx_id=0, det_size=(640, 640))
        logger.info("[InsightFace] Model loaded")
    return _insight_app

# ---------------------------------------------------------------------------
# Image I/O
# ---------------------------------------------------------------------------

def save_image(file_storage, category: str) -> str:
    if not hasattr(file_storage, "save"):
        raise ValueError("file_storage must be a Werkzeug FileStorage object")

    _ensure_dirs()
    dest_dir = MISSING_IMG_DIR if category == "missing" else FOUND_IMG_DIR

    ext      = os.path.splitext(file_storage.filename or "")[1].lower() or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    abs_path = os.path.join(dest_dir, filename)

    file_storage.save(abs_path)

    if not os.path.exists(abs_path):
        raise IOError(f"Image was not saved to {abs_path}")

    rel_path = f"static/uploads/{category}/{filename}"
    logger.debug("[SAVE] Image saved → %s", rel_path)
    return rel_path


# ---------------------------------------------------------------------------
# Embedding extraction
# ---------------------------------------------------------------------------

def extract_embedding(image_path: str) -> Optional[np.ndarray]:
    full_path = os.path.join(BASE_DIR, image_path) if not os.path.isabs(image_path) else image_path
    img = cv2.imread(full_path)
    if img is None:
        logger.warning("[EMBED] Cannot read image: %s", full_path)
        return None

    app   = _get_insight_app()
    faces = app.get(img)

    if not faces:
        h, w      = img.shape[:2]
        pad       = int(max(h, w) * 0.3)
        img_padded = cv2.copyMakeBorder(
            img, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=(0, 0, 0)
        )
        faces = app.get(img_padded)

    if not faces:
        logger.info("[EMBED] No face detected in: %s", full_path)
        return None

    # Pick the face with the highest detection confidence ___change this
    face = max(faces, key=lambda f: f.det_score)
    embedding = face.normed_embedding.astype(np.float32)
    return embedding


# ---------------------------------------------------------------------------
# Sanitisation
# ---------------------------------------------------------------------------

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

    # default: str
    return str(value).strip() or None


# ---------------------------------------------------------------------------
# Database lookup helpers
# ---------------------------------------------------------------------------

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

