"""
app/routes/missing_person.py
============================
Blueprint: Missing Person Reports

Endpoints:
    POST /missing-report/send          Submit a missing-person report
    POST /report/<found_id>/validate   Confirm or reject an UNCERTAIN match

Matching thresholds:
    ≥ 0.677  → MATCH     (auto-confirmed, persisted to DB + FAISS)
    ≥ 0.60   → UNCERTAIN (saved to DB only, awaits human validation)
    < 0.60   → NO_MATCH  (persisted to DB + FAISS, no candidate)

Unified response shape:
    {
        "success": bool,
        "status":  "match" | "uncertain" | "no_match" | "error",
        "data":    dict | null,
        "message": str
    }
"""

from __future__ import annotations

import logging
import traceback

import MySQLdb.cursors
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..extensions import mysql
from ..services.face_service import (
    add_embedding_to_index,
    attach_image_url,
    build_image_url,
    extract_embedding,
    get_found_person_by_faiss_id,
    sanitize_value,
    save_image,
    search_faiss_index,
)

logger = logging.getLogger(__name__)

missing_person_bp = Blueprint("missing_person", __name__)

MATCH_THRESHOLD     = 0.677
UNCERTAIN_THRESHOLD = 0.60


# ─────────────────────────────────────────────────────────────────────────────
# Response helpers
# ─────────────────────────────────────────────────────────────────────────────

def _resp(success: bool, status: str, data: dict | None, message: str, http: int):
    return jsonify({"success": success, "status": status, "data": data, "message": message}), http

def _ok(status: str, data: dict, message: str = ""):
    return _resp(True, status, data, message, 200)

def _created(status: str, data: dict, message: str = ""):
    return _resp(True, status, data, message, 201)

def _err(message: str, http: int = 400):
    return _resp(False, "error", None, message, http)


# ─────────────────────────────────────────────────────────────────────────────
# DB helper — insert missing_person row (no faiss_id yet)
# ─────────────────────────────────────────────────────────────────────────────

def _db_insert_missing(cur, user_id: int, fields: dict, image_path: str) -> int:
    """
    Insert into missing_persons. faiss_id is set later via UPDATE.
    Returns the new primary key.
    """
    cur.execute(
        """
        INSERT INTO missing_persons
            (user_id, full_name, approximate_age, gender,
             last_seen_location, last_seen_date,
             phone_number1, phone_number2, image_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            user_id,
            sanitize_value(fields.get("full_name", "Unknown")),
            sanitize_value(fields.get("age"),                "int"),
            sanitize_value(fields.get("gender")),
            sanitize_value(fields.get("last_seen_location")),
            sanitize_value(fields.get("last_seen_date")),
            sanitize_value(fields.get("phone_number1"),      "phone"),
            sanitize_value(fields.get("phone_number2"),      "phone"),
            image_path,
        ),
    )
    return cur.lastrowid


# ─────────────────────────────────────────────────────────────────────────────
# POST /missing-report/send
# ─────────────────────────────────────────────────────────────────────────────

@missing_person_bp.route("/missing-report/send", methods=["POST"])
@jwt_required()
def send_missing_report():
    # ── Identity ──────────────────────────────────────────────────────────────
    # Swap for get_jwt_identity() once JWT carries the real user_id
    user_id: int = 6

    # ── Validate required fields ──────────────────────────────────────────────
    required = ["full_name", "age", "gender", "phone_number1", "phone_number2"]
    missing  = [f for f in required if not (request.form.get(f) or "").strip()]
    if missing:
        return _err(f"Missing required fields: {', '.join(missing)}")

    image_file = request.files.get("image_path")
    if not image_file or not image_file.filename:
        return _err("Image file is required.")

    fields = {
        "full_name":          request.form["full_name"].strip(),
        "age":                request.form.get("age", "").strip(),
        "gender":             request.form["gender"].strip(),
        "last_seen_location": request.form.get("last_seen_location", "").strip(),
        "last_seen_date":     request.form.get("last_seen_date", "").strip(),
        "phone_number1":      (request.form.get("phone_number1") or "").strip(),
        "phone_number2":      (request.form.get("phone_number2") or "").strip(),
    }

    # ── Save image & extract embedding ────────────────────────────────────────
    try:
        image_path: str = save_image(image_file, category="missing")
        embedding        = extract_embedding(image_path)
    except Exception:
        logger.exception("Image save/embedding failed")
        return _err("Image processing failed.", 500)

    if embedding is None:
        return _err("No face detected in the uploaded image.", 422)

    # ── Search FAISS (found index) ────────────────────────────────────────────
    try:
        distances, indices = search_faiss_index(embedding, category="found", top_k=1)
    except Exception:
        logger.exception("FAISS search failed")
        return _err("Face search service error.", 500)

    # Resolve score & FAISS id safely
    similarity: float | None = None
    faiss_id:   int   | None = None

    if distances is not None and indices is not None:
        raw_idx = int(indices[0][0])
        if raw_idx >= 0:                        # -1 means empty index
            similarity = float(distances[0][0])
            faiss_id   = raw_idx

    # ── Decide ────────────────────────────────────────────────────────────────
    is_match     = similarity is not None and similarity >= MATCH_THRESHOLD
    is_uncertain = (
        not is_match
        and similarity is not None
        and similarity >= UNCERTAIN_THRESHOLD
    )

    # ══════════════════════════════════════════════════════════════════════════
    # MATCH
    # ══════════════════════════════════════════════════════════════════════════
    if is_match:
        matched = get_found_person_by_faiss_id(mysql, faiss_id)

        if not matched:
            logger.warning(
                "MATCH score %.4f but faiss_id=%s absent from DB — treating as NO_MATCH",
                similarity, faiss_id,
            )
            is_match = False           # fall through to NO_MATCH below
        else:
            cur = None
            try:
                cur = mysql.connection.cursor()

                new_faiss_id   = add_embedding_to_index(embedding, category="missing")
                new_missing_id = _db_insert_missing(cur, user_id, fields, image_path)

                cur.execute(
                    "UPDATE missing_persons SET faiss_id = %s WHERE missing_id = %s",
                    (new_faiss_id, new_missing_id),
                )
                cur.execute(
                    """
                    INSERT INTO match_results
                        (missing_id, found_id, user_id, similarity_score, status)
                    VALUES (%s, %s, %s, %s, 'confirmed')
                    """,
                    (new_missing_id, matched["found_id"], user_id, similarity),
                )
                mysql.connection.commit()

            except Exception:
                if cur:
                    mysql.connection.rollback()
                logger.exception("DB error — MATCH persist")
                return _err("Database error while saving match.", 500)
            finally:
                if cur:
                    cur.close()

            return _ok("match", {
                "missing_id": new_missing_id,
                "match_id":   matched["found_id"],
                "percentage": round(similarity, 4),
                "matched_person": attach_image_url(matched),
            }, "Match found.")

    # ══════════════════════════════════════════════════════════════════════════
    # UNCERTAIN
    # ══════════════════════════════════════════════════════════════════════════
    if is_uncertain:
        candidate = get_found_person_by_faiss_id(mysql, faiss_id)

        if not candidate:
            logger.warning(
                "UNCERTAIN score %.4f but faiss_id=%s absent from DB — treating as NO_MATCH",
                similarity, faiss_id,
            )
            is_uncertain = False       # fall through to NO_MATCH below
        else:
            cur = None
            try:
                cur = mysql.connection.cursor()
                # NO FAISS here — wait for human validation
                new_missing_id = _db_insert_missing(cur, user_id, fields, image_path)
                mysql.connection.commit()

            except Exception:
                if cur:
                    mysql.connection.rollback()
                logger.exception("DB error — UNCERTAIN persist")
                return _err("Database error while saving report.", 500)
            finally:
                if cur:
                    cur.close()

            return _ok("uncertain", {
                "missing_id": new_missing_id,
                "match_id":   candidate["found_id"],
                "percentage": round(similarity, 4),
                "image_url":  build_image_url(image_path),
                "candidate":  attach_image_url(candidate),
            }, "Possible match found. Please validate.")

    # ══════════════════════════════════════════════════════════════════════════
    # NO MATCH
    # ══════════════════════════════════════════════════════════════════════════
    cur = None
    try:
        cur = mysql.connection.cursor()

        new_faiss_id   = add_embedding_to_index(embedding, category="missing")
        new_missing_id = _db_insert_missing(cur, user_id, fields, image_path)

        cur.execute(
            "UPDATE missing_persons SET faiss_id = %s WHERE missing_id = %s",
            (new_faiss_id, new_missing_id),
        )
        mysql.connection.commit()

    except Exception:
        if cur:
            mysql.connection.rollback()
        logger.exception("DB error — NO_MATCH persist")
        return _err("Database error while saving report.", 500)
    finally:
        if cur:
            cur.close()

    return _created("no_match", {
        "missing_id": new_missing_id,
        "image_url":  build_image_url(image_path),
    }, "Report submitted. No match found.")


# ─────────────────────────────────────────────────────────────────────────────
# POST /report/<found_id>/validate
# ─────────────────────────────────────────────────────────────────────────────

@missing_person_bp.route("/report/<int:found_id>/validate", methods=["POST"])
@jwt_required()
def validate_match(found_id: int):
    """
    Resolve an UNCERTAIN result for a missing-person report.

    URL param:
        found_id   — the found_person candidate (returned as match_id in /send)

    Body (JSON):
        {
            "decision":   "confirmed" | "rejected",
            "percentage": 0.63,
            "missing_id": 42
        }
    """
    user_id: int = 6  # get_jwt_identity()

    body = request.get_json(silent=True) or {}
    decision:   str        = (body.get("decision") or "").strip()
    similarity: float      = float(body.get("percentage") or 0)
    missing_id: int | None = body.get("missing_id")

    if decision not in ("confirmed", "rejected"):
        return _err("decision must be 'confirmed' or 'rejected'.")
    if not missing_id:
        return _err("missing_id is required.")

    status_val = "confirmed" if decision == "confirmed" else "no_match"

    cur = None
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Verify missing_id exists and fetch image_path
        cur.execute(
            "SELECT missing_id, image_path FROM missing_persons WHERE missing_id = %s",
            (missing_id,),
        )
        row = cur.fetchone()
        if not row:
            return _err(f"missing_id {missing_id} not found.", 404)

        image_path: str = (row.get("image_path") or "")

        # Add to FAISS regardless of decision (rejected = still a real person)
        if image_path:
            embedding = extract_embedding(image_path)
            if embedding is not None:
                new_faiss_id = add_embedding_to_index(embedding, category="missing")
                cur.execute(
                    "UPDATE missing_persons SET faiss_id = %s WHERE missing_id = %s",
                    (new_faiss_id, missing_id),
                )

        # Record decision in match_results
        cur.execute(
            """
            INSERT INTO match_results
                (missing_id, found_id, user_id, similarity_score, status)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (missing_id, found_id, user_id, similarity, status_val),
        )
        mysql.connection.commit()

    except Exception:
        if cur:
            mysql.connection.rollback()
        logger.exception("DB error — validate_match")
        return _err("Database error during validation.", 500)
    finally:
        if cur:
            cur.close()

    msg = "Match confirmed." if decision == "confirmed" else "Match rejected. Report saved independently."
    return _ok(status_val, {"missing_id": missing_id, "found_id": found_id}, msg)