"""
app/routes/found_person.py
==========================
Blueprint: Found Person Reports

Endpoints:
    POST /found-report/send              Submit a found-person report
    POST /report/<missing_id>/validate   Confirm or reject an UNCERTAIN match

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

import MySQLdb.cursors
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ..extensions import mysql
from ..services.face_service import (
    add_embedding_to_index,
    attach_image_url,
    build_image_url,
    extract_embedding,
    get_missing_person_by_faiss_id,
    sanitize_value,
    save_image,
    search_faiss_index,
)

logger = logging.getLogger(__name__)

found_person_bp = Blueprint("found_person", __name__)

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
# DB helper — insert found_person row (no faiss_id yet)
# ─────────────────────────────────────────────────────────────────────────────

def _db_insert_found(cur, organization_id: int, fields: dict, image_path: str) -> int:
    """
    Insert into found_persons. faiss_id is set later via UPDATE.
    Returns the new primary key.
    """
    cur.execute(
        """
        INSERT INTO found_persons
            (organization_id, full_name, approximate_age, gender,
             found_location, found_date, health_status, image_path,
             phone_number1, phone_number2)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            organization_id,
            sanitize_value(fields.get("full_name", "Unknown")),
            sanitize_value(fields.get("approximate_age"), "int"),
            sanitize_value(fields.get("gender")),
            sanitize_value(fields.get("found_location")),
            sanitize_value(fields.get("found_date")),
            sanitize_value(fields.get("health_status")),
            image_path,
            sanitize_value(fields.get("phone_number1"),   "phone"),
            sanitize_value(fields.get("phone_number2"),   "phone"),
        ),
    )
    return cur.lastrowid


# ─────────────────────────────────────────────────────────────────────────────
# POST /found-report/send
# ─────────────────────────────────────────────────────────────────────────────

@found_person_bp.route("/found-report/send", methods=["POST"])
@jwt_required()
def send_found_report():
    # ── Identity ──────────────────────────────────────────────────────────────
    organization_id: int = 5  # get_jwt_identity()

    # ── Validate required fields ──────────────────────────────────────────────
    required = ["phone_number1", "phone_number2"]
    missing  = [f for f in required if not (request.form.get(f) or "").strip()]
    if missing:
        return _err(f"Missing required fields: {', '.join(missing)}")

    image_file = request.files.get("image_path")
    if not image_file or not image_file.filename:
        return _err("Image file is required.")

    fields = {
        "full_name":       request.form.get("full_name", "Unknown").strip(),
        "approximate_age": request.form.get("approximate_age", "").strip(),
        "gender":          request.form.get("gender", "").strip(),
        "found_location":  request.form.get("found_location", "").strip(),
        "found_date":      request.form.get("found_date", "").strip(),
        "health_status":   request.form.get("health_status", "").strip(),
        "phone_number1":   (request.form.get("phone_number1") or "").strip(),
        "phone_number2":   (request.form.get("phone_number2") or "").strip(),
    }

    # ── Save image & extract embedding ────────────────────────────────────────
    try:
        image_path: str = save_image(image_file, category="found")
        embedding        = extract_embedding(image_path)
    except Exception:
        logger.exception("Image save/embedding failed")
        return _err("Image processing failed.", 500)

    if embedding is None:
        return _err("No face detected in the uploaded image.", 422)

    # ── Search FAISS (missing index) ──────────────────────────────────────────
    try:
        distances, indices = search_faiss_index(embedding, category="missing", top_k=1)
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
        matched = get_missing_person_by_faiss_id(mysql, faiss_id)

        if not matched:
            logger.warning(
                "MATCH score %.4f but faiss_id=%s absent from DB — treating as NO_MATCH",
                similarity, faiss_id,
            )
            is_match = False           # fall through to NO_MATCH
        else:
            cur = None
            try:
                cur = mysql.connection.cursor()

                new_faiss_id = add_embedding_to_index(embedding, category="found")
                new_found_id = _db_insert_found(cur, organization_id, fields, image_path)

                cur.execute(
                    "UPDATE found_persons SET faiss_id = %s WHERE found_id = %s",
                    (new_faiss_id, new_found_id),
                )
                cur.execute(
                    """
                    INSERT INTO match_results
                        (missing_id, found_id, organization_id, similarity_score, status)
                    VALUES (%s, %s, %s, %s, 'confirmed')
                    """,
                    (matched["missing_id"], new_found_id, organization_id, similarity),
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
                "found_id":   new_found_id,
                "match_id":   matched["missing_id"],
                "percentage": round(similarity, 4),
                "matched_person": attach_image_url(matched),
            }, "Match found.")

    # ══════════════════════════════════════════════════════════════════════════
    # UNCERTAIN
    # ══════════════════════════════════════════════════════════════════════════
    if is_uncertain:
        candidate = get_missing_person_by_faiss_id(mysql, faiss_id)

        if not candidate:
            logger.warning(
                "UNCERTAIN score %.4f but faiss_id=%s absent from DB — treating as NO_MATCH",
                similarity, faiss_id,
            )
            is_uncertain = False       # fall through to NO_MATCH
        else:
            cur = None
            try:
                cur = mysql.connection.cursor()
                # NO FAISS here — wait for human validation
                new_found_id = _db_insert_found(cur, organization_id, fields, image_path)
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
                "found_id":  new_found_id,
                "match_id":  candidate["missing_id"],
                "percentage": round(similarity, 4),
                "image_url": build_image_url(image_path),
                "candidate": attach_image_url(candidate),
            }, "Possible match found. Please validate.")

    # ══════════════════════════════════════════════════════════════════════════
    # NO MATCH
    # ══════════════════════════════════════════════════════════════════════════
    cur = None
    try:
        cur = mysql.connection.cursor()

        new_faiss_id = add_embedding_to_index(embedding, category="found")
        new_found_id = _db_insert_found(cur, organization_id, fields, image_path)

        cur.execute(
            "UPDATE found_persons SET faiss_id = %s WHERE found_id = %s",
            (new_faiss_id, new_found_id),
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
        "found_id":  new_found_id,
        "image_url": build_image_url(image_path),
    }, "Report submitted. No match found.")


# ─────────────────────────────────────────────────────────────────────────────
# POST /report/<missing_id>/validate
# ─────────────────────────────────────────────────────────────────────────────

@found_person_bp.route("/report/<int:missing_id>/validate", methods=["POST"])
@jwt_required()
def validate_found_match(missing_id: int):
    """
    Resolve an UNCERTAIN result for a found-person report.

    URL param:
        missing_id   — the missing_person candidate (returned as match_id in /send)

    Body (JSON):
        {
            "decision":  "confirmed" | "rejected",
            "percentage": 0.63,
            "found_id":  17
        }
    """
    organization_id: int = 5  # get_jwt_identity()

    body = request.get_json(silent=True) or {}
    decision:   str        = (body.get("decision") or "").strip()
    similarity: float      = float(body.get("percentage") or 0)
    found_id:   int | None = body.get("found_id")

    if decision not in ("confirmed", "rejected"):
        return _err("decision must be 'confirmed' or 'rejected'.")
    if not found_id:
        return _err("found_id is required.")

    status_val = "confirmed" if decision == "confirmed" else "no_match"

    cur = None
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Verify found_id exists and fetch image_path
        cur.execute(
            "SELECT found_id, image_path FROM found_persons WHERE found_id = %s",
            (found_id,),
        )
        row = cur.fetchone()
        if not row:
            return _err(f"found_id {found_id} not found.", 404)

        image_path: str = (row.get("image_path") or "")

        # Add to FAISS regardless of decision
        if image_path:
            embedding = extract_embedding(image_path)
            if embedding is not None:
                new_faiss_id = add_embedding_to_index(embedding, category="found")
                cur.execute(
                    "UPDATE found_persons SET faiss_id = %s WHERE found_id = %s",
                    (new_faiss_id, found_id),
                )

        # Record decision in match_results
        cur.execute(
            """
            INSERT INTO match_results
                (missing_id, found_id, organization_id, similarity_score, status)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (missing_id, found_id, organization_id, similarity, status_val),
        )
        mysql.connection.commit()

    except Exception:
        if cur:
            mysql.connection.rollback()
        logger.exception("DB error — validate_found_match")
        return _err("Database error during validation.", 500)
    finally:
        if cur:
            cur.close()

    msg = "Match confirmed." if decision == "confirmed" else "Match rejected. Report saved independently."
    return _ok(status_val, {"found_id": found_id, "missing_id": missing_id}, msg)