"""
app/services/face_service.py
============================
Core utilities:
  - Image I/O
  - Face embedding extraction (InsightFace)
  - FAISS index management (in-memory cache + disk persistence)
  - Database lookup helpers
  - Sanitisation helpers

All functions are stateless except for the module-level FAISS cache
and InsightFace singleton — both are thread-safe for read-heavy workloads.
"""

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
BASE_URL           = os.environ.get("BASE_URL", "http://localhost:5000")

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
    """
    Normalize, add to FAISS, persist to disk.

    Returns:
        faiss_id (0-based sequential position in index).
    """
    index = load_faiss_index(category)
    vec   = embedding.astype(np.float32).reshape(1, -1)
    faiss.normalize_L2(vec)
    index.add(vec)
    faiss_id = index.ntotal - 1
    _save_faiss_index(index, category)
    logger.debug("[FAISS] Added to '%s' index → faiss_id=%d", category, faiss_id)
    return faiss_id


def search_faiss_index(
    embedding: np.ndarray, category: str, top_k: int = 1
) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    """
    Search top_k nearest neighbours.

    Returns:
        (distances, indices) shaped (1, top_k), or (None, None) if index empty.
    """
    index = load_faiss_index(category)
    if index.ntotal == 0:
        logger.warning("[FAISS] '%s' index is empty — skipping search", category)
        return None, None

    vec = embedding.astype(np.float32).reshape(1, -1)
    faiss.normalize_L2(vec)
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
    """
    Persist an uploaded image to disk.

    Returns:
        Relative URL path  e.g. "static/uploads/missing/abc123.jpg"

    Raises:
        ValueError if file_storage is not a valid FileStorage object.
        IOError    if saving fails.
    """
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


def build_image_url(path: str) -> Optional[str]:
    """Convert a relative image path to a full URL."""
    if not path:
        return None
    clean = path.lstrip("/")
    return f"{BASE_URL}/{clean}"


def attach_image_url(data: dict) -> dict:
    """
    Return a shallow copy of `data` with image_path converted to a full URL.
    Does NOT mutate the original dict.
    """
    if not data:
        return data
    result = dict(data)
    raw = result.get("image_path")
    if raw and not str(raw).startswith("http"):
        result["image_path"] = f"{BASE_URL}/{str(raw).lstrip('/')}"
    return result


# ---------------------------------------------------------------------------
# Embedding extraction
# ---------------------------------------------------------------------------

def extract_embedding(image_path: str) -> Optional[np.ndarray]:
    """
    Extract a normalised face embedding from an image on disk.

    Tries twice: first on the raw image, then with black padding applied
    (helps when the face is close to the edge).

    Returns:
        np.ndarray of shape (512,) or None if no face detected.
    """
    full_path = os.path.join(BASE_DIR, image_path) if not os.path.isabs(image_path) else image_path
    img = cv2.imread(full_path)
    if img is None:
        logger.warning("[EMBED] Cannot read image: %s", full_path)
        return None

    app   = _get_insight_app()
    faces = app.get(img)

    # Retry with padding
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

    # Pick the face with the highest detection confidence
    face      = max(faces, key=lambda f: f.det_score)
    embedding = face.normed_embedding.astype(np.float32)
    # Ensure L2-normalised for cosine similarity via IndexFlatIP
    faiss.normalize_L2(embedding.reshape(1, -1))
    return embedding


# ---------------------------------------------------------------------------
# Sanitisation
# ---------------------------------------------------------------------------

def sanitize_value(value, expected_type: str = "str"):
    """
    Clean a raw form value before inserting into MySQL.

    Args:
        value:         Raw value from request.form
        expected_type: "str" | "int" | "phone"

    Returns:
        Sanitised value or None.

    Raises:
        ValueError if a FileStorage object is passed by mistake.
    """
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
    """
    Fetch a missing_person row by its FAISS index position.

    Returns dict or None.
    """
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(
            """
            SELECT missing_id, full_name, approximate_age, gender,
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
    """
    Fetch a found_person row (with authority name) by its FAISS index position.

    Returns dict or None.
    """
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
            WHERE  fp.faiss_id = %s
            LIMIT  1
            """,
            (faiss_id,),
        )
        row = cur.fetchone()
        cur.close()
        return row
    except Exception:
        logger.exception("[DB] get_found_person_by_faiss_id failed for faiss_id=%s", faiss_id)
        return None


def get_user_id_by_identity(mysql, identity: str) -> Optional[int]:
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(
            "SELECT id FROM users WHERE email_or_phone = %s LIMIT 1", (identity,)
        )
        row = cur.fetchone()
        cur.close()
        return row["id"] if row else None
    except Exception:
        logger.exception("[DB] get_user_id_by_identity failed")
        return None


def get_authority_id_by_identity(mysql, identity: str) -> Optional[int]:
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute(
            "SELECT organization_id FROM authority WHERE email_or_phone = %s LIMIT 1",
            (identity,),
        )
        row = cur.fetchone()
        cur.close()
        return row["organization_id"] if row else None
    except Exception:
        logger.exception("[DB] get_authority_id_by_identity failed")
        return None