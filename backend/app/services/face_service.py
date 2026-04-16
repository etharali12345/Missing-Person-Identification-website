from flask import request
import os
import uuid
import traceback
import numpy as np
import faiss
import cv2
from typing import Tuple, Union, Optional
import MySQLdb.cursors

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
UPLOAD_BASE_DIR    = os.environ.get("UPLOAD_BASE_DIR", "static/uploads")
MISSING_IMG_DIR    = os.path.join(UPLOAD_BASE_DIR, "missing")
FOUND_IMG_DIR      = os.path.join(UPLOAD_BASE_DIR, "found")
MISSING_FAISS_PATH = os.environ.get("MISSING_FAISS_PATH", "faiss_indexes/missing_persons.index")
FOUND_FAISS_PATH   = os.environ.get("FOUND_FAISS_PATH",   "faiss_indexes/found_persons.index")
FACE_EMBEDDING_DIM = 512

# ---------------------------------------------------------------------------
# ✅ FAISS index cache في memory (من الكود القديم) - أسرع بكثير
# ---------------------------------------------------------------------------
_faiss_cache = {}

def ensure_dirs():
    for d in (MISSING_IMG_DIR, FOUND_IMG_DIR,
              os.path.dirname(MISSING_FAISS_PATH),
              os.path.dirname(FOUND_FAISS_PATH)):
        os.makedirs(d, exist_ok=True)

def _faiss_index_path(category: str) -> str:
    if category == "missing": return MISSING_FAISS_PATH
    if category == "found":   return FOUND_FAISS_PATH
    raise ValueError(f"Unknown FAISS category: {category!r}")

def load_faiss_index(category: str) -> faiss.Index:
    """تحميل الـ index من الـ cache أو من disk إذا لم يكن محملاً."""
    if category in _faiss_cache:
        return _faiss_cache[category]         # ✅ من memory مباشرة

    path = _faiss_index_path(category)
    if os.path.exists(path):
        index = faiss.read_index(path)
    else:
        ensure_dirs()
        index = faiss.IndexFlatIP(FACE_EMBEDDING_DIM)

    _faiss_cache[category] = index            # ✅ احفظه في الـ cache
    return index

def save_faiss_index(index: faiss.Index, category: str) -> None:
    path = _faiss_index_path(category)
    ensure_dirs()
    faiss.write_index(index, path)
    _faiss_cache[category] = index            # ✅ حدّث الـ cache

def add_embedding_to_index(embedding: np.ndarray, category: str) -> None:
    index = load_faiss_index(category)
    vec   = embedding.astype(np.float32).reshape(1, -1)
    faiss.normalize_L2(vec)
    index.add(vec)
    save_faiss_index(index, category)         # ✅ يحفظ ويحدّث الـ cache

def search_faiss_index(embedding: np.ndarray, category: str, top_k: int = 1) -> Tuple[np.ndarray, np.ndarray]:
    index = load_faiss_index(category)
    print(f"[FAISS] category='{category}' | total vectors = {index.ntotal}")

    if index.ntotal == 0:
        print("[FAISS] ⚠️ الـ index فاضي!")
        return None, None

    vec = embedding.astype(np.float32).reshape(1, -1)
    faiss.normalize_L2(vec)
    distances, indices = index.search(vec, top_k)
    print(f"[FAISS] similarity={distances[0][0]:.4f} | index row={indices[0][0]}")
    return distances, indices

# ---------------------------------------------------------------------------
# Image helpers
# ---------------------------------------------------------------------------
def build_image_url(path: str) -> str:
    if not path:
        return None
    base_url = request.host_url.rstrip('/')
    return base_url + "/" + path.lstrip("/")


def attach_image_url(data: dict) -> dict:
    if data and data.get("image_path"):
        data["image_url"] = build_image_url(data["image_path"])
    return data
def save_image(file_storage, category: str) -> str:
    ensure_dirs()
    dest_dir = MISSING_IMG_DIR if category == "missing" else FOUND_IMG_DIR
    ext      = os.path.splitext(file_storage.filename)[1].lower() or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    abs_path = os.path.join(dest_dir, filename)
    file_storage.save(abs_path)
    return os.path.join("static/uploads", category, filename).replace("\\", "/")

# ---------------------------------------------------------------------------
# ✅ Face extraction محسّن (من الكود القديم) - يدعم padding لو مفيش وجه
# ---------------------------------------------------------------------------
_INSIGHT_APP = None

def get_insight_app():
    global _INSIGHT_APP
    if _INSIGHT_APP is None:
        from insightface.app import FaceAnalysis
        _INSIGHT_APP = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
        _INSIGHT_APP.prepare(ctx_id=0, det_size=(640, 640))
    return _INSIGHT_APP

def extract_embedding(image_path: str) -> Union[np.ndarray, None]:
    """
    استخراج الـ embedding مع دعم padding لو الوجه مش واضح (من الكود القديم).
    """
    img = cv2.imread(image_path)
    if img is None:
        return None

    app   = get_insight_app()
    faces = app.get(img)

    # ✅ لو مفيش وجه، جرّب مع padding (من الكود القديم)
    if not faces:
        h, w      = img.shape[:2]
        pad_ratio = 0.3
        img = cv2.copyMakeBorder(
            img,
            int(h * pad_ratio), int(h * pad_ratio),
            int(w * pad_ratio), int(w * pad_ratio),
            cv2.BORDER_CONSTANT, value=(0, 0, 0)
        )
        faces = app.get(img)

    if not faces:
        return None

    # ✅ اختار أوضح وجه (أعلى det_score)
    face      = max(faces, key=lambda f: f.det_score)
    embedding = face.normed_embedding.astype(np.float32)
    faiss.normalize_L2(embedding.reshape(1, -1))  # تأكد من التطبيع
    return embedding

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
def sanitize_value(value, expected_type="str"):
    """
    تنظيف القيم قبل إدخالها في DB.
    - يمنع تخزين FileStorage objects
    - يحول empty strings لـ None
    - يتحقق من الأنواع
    """
    # ✅ منع تخزين FileStorage objects
    if hasattr(value, 'read') or hasattr(value, 'filename'):
        raise ValueError(f"FileStorage object passed instead of path string!")
    
    if value is None or value == "" or value == 0:
        return None
        
    if expected_type == "int":
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
            
    if expected_type == "str":
        return str(value).strip() or None
        
    return value
def get_missing_person_by_faiss_id(mysql, faiss_index: int) -> Optional[dict]:
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(
            """
            SELECT missing_id, full_name, approximate_age, gender,
                   last_seen_date, last_seen_location, image_path,
                   phone_number1, phone_number2, faiss_id
            FROM   missing_persons
            WHERE  faiss_id IS NOT NULL
            ORDER  BY missing_id ASC
            LIMIT  1 OFFSET %s
            """,
            (faiss_index,)
        )
        row = cur.fetchone()
        cur.close()
        print(f"[DEBUG] faiss_index={faiss_index} → missing={row}")
        return row
    except Exception:
        traceback.print_exc()
        return None

def get_found_person_by_faiss_id(mysql, faiss_index: int) -> Optional[dict]:
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(
            """
            SELECT fp.found_id, fp.full_name, fp.approximate_age, fp.gender,
                   fp.health_status, fp.found_date, fp.found_location,
                   fp.image_path, fp.phone_number1, fp.phone_number2,
                   fp.faiss_id, a.authority_name
            FROM   found_persons fp
            LEFT JOIN authority a ON fp.organization_id = a.organization_id
            WHERE  fp.faiss_id IS NOT NULL
            ORDER  BY fp.found_id ASC
            LIMIT  1 OFFSET %s
            """,
            (faiss_index,)
        )
        row = cur.fetchone()
        cur.close()
        print(f"[DEBUG] faiss_index={faiss_index} → found={row}")
        return row
    except Exception:
        traceback.print_exc()
        return None

def get_user_id_by_identity(mysql, identity: str) -> Optional[int]:
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT id FROM users WHERE email_or_phone = %s LIMIT 1", (identity,))
        row = cur.fetchone()
        cur.close()
        return row["id"] if row else None
    except Exception:
        traceback.print_exc()
        return None

def get_authority_id_by_identity(mysql, identity: str) -> Optional[int]:
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT organization_id FROM authority WHERE email_or_phone = %s LIMIT 1", (identity,))
        row = cur.fetchone()
        cur.close()
        return row["organization_id"] if row else None
    except Exception:
        traceback.print_exc()
        return None