from __future__ import annotations
import logging
import MySQLdb.cursors
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from ..extensions import mysql
from ..services.face_service import (
    add_embedding_to_index,
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
    response = {"status": status}
    if data:
        response.update(data)
    return jsonify(response), http

def _ok(status: str, data: dict, message: str = ""):
    return _resp(True, status, data, message, 200)

def _created(status: str, data: dict, message: str = ""):
    return _resp(True, status, data, message, 201)

def _err(message: str, http: int = 400):
    return _resp(False, "error", None, message, http)


# ─────────────────────────────────────────────────────────────────────────────
# DB helpers
# ─────────────────────────────────────────────────────────────────────────────

def _db_insert_found(cur, uploader_id: int, role: str, fields: dict, image_path: str) -> int:
    if role == "admin":
        authority_id_val  = None
        admin_id_val      = uploader_id
    else:
        authority_id_val  = uploader_id
        admin_id_val      = None

    cur.execute(
        """
        INSERT INTO found_persons
            (authority_id, uploaded_by_admin_id,
             full_name, approximate_age, gender,
             found_location, found_date, health_status, image_path,
             phone_number1, phone_number2)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            authority_id_val,
            admin_id_val,
            sanitize_value(fields.get("full_name", "Unknown")),
            sanitize_value(fields.get("approximate_age"), "int"),
            sanitize_value(fields.get("gender")),
            sanitize_value(fields.get("found_location")),
            sanitize_value(fields.get("found_date")),
            sanitize_value(fields.get("health_status")),
            image_path,
            sanitize_value(fields.get("phone_number1"), "phone"),
            sanitize_value(fields.get("phone_number2"), "phone"),
        ),
    )
    return cur.lastrowid


def _db_insert_match_result(cur, missing_id: int, found_id: int, similarity: float, status: str) -> int:
    cur.execute(
        """
        INSERT INTO match_results
            (missing_id, found_id, similarity_score, status)
        VALUES (%s, %s, %s, %s)
        """,
        (missing_id, found_id, similarity, status),
    )
    return cur.lastrowid


def _owner_col(role: str) -> str:
    return "uploaded_by_admin_id" if role == "admin" else "authority_id"


# ─────────────────────────────────────────────────────────────────────────────
# POST /found-report/send
# ─────────────────────────────────────────────────────────────────────────────

@found_person_bp.route("/found-report/send", methods=["POST"])
@jwt_required()
def send_found_report():
    current_identity = get_jwt_identity()
    uploader_id = current_identity.get("id")
    role        = current_identity.get("role")

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

    try:
        image_path: str = save_image(image_file, category="found")
        embedding        = extract_embedding(image_path)
    except Exception:
        logger.exception("Image save/embedding failed")
        return _err("Image processing failed.", 500)

    if embedding is None:
        return _err("No face detected in the uploaded image.", 422)

    try:
        distances, indices = search_faiss_index(embedding, category="missing", top_k=1)
    except Exception:
        logger.exception("FAISS search failed")
        return _err("Face search service error.", 500)

    similarity: float | None = None
    faiss_id:   int   | None = None

    if distances is not None and indices is not None:
        raw_idx = int(indices[0][0])
        if raw_idx >= 0:
            sim        = float(distances[0][0])
            similarity = (sim + 1) / 2
            faiss_id   = raw_idx

    is_match = similarity is not None and similarity >= MATCH_THRESHOLD
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
            is_match = False       
        else:
            cur = None
            try:
                cur = mysql.connection.cursor()

                new_faiss_id = add_embedding_to_index(embedding, category="found")
                new_found_id = _db_insert_found(cur, uploader_id, role, fields, image_path)
                cur.execute(
                    "UPDATE found_persons SET faiss_id = %s WHERE found_id = %s",
                    (new_faiss_id, new_found_id),
                )

                match_result_id = _db_insert_match_result(
                    cur, matched["missing_id"], new_found_id, similarity, "match"
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
                "matchId":    match_result_id,
                "percentage": round(similarity, 4),
                "details":    matched,
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
            is_uncertain = False
        else:
            cur = None
            try:
                cur = mysql.connection.cursor()

                new_faiss_id = add_embedding_to_index(embedding, category="found")
                new_found_id = _db_insert_found(cur, uploader_id, role, fields, image_path)
                cur.execute(
                    "UPDATE found_persons SET faiss_id = %s WHERE found_id = %s",
                    (new_faiss_id, new_found_id),
                )

                match_result_id = _db_insert_match_result(
                    cur, candidate["missing_id"], new_found_id, similarity, "uncertain"
                )
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
                "found_id":   new_found_id,
                "matchId":    match_result_id,
                "percentage": round(similarity, 4),
                "details":    candidate,
            }, "Possible match found. Please validate.")

    # ══════════════════════════════════════════════════════════════════════════
    # NO MATCH
    # ══════════════════════════════════════════════════════════════════════════
    cur = None
    try:
        cur = mysql.connection.cursor()

        new_faiss_id = add_embedding_to_index(embedding, category="found")
        new_found_id = _db_insert_found(cur, uploader_id, role, fields, image_path)
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
        "found_id": new_found_id,
    }, "Report submitted. No match found.")


# ─────────────────────────────────────────────────────────────────────────────
# POST /found-report/<match_id>/validate
# ─────────────────────────────────────────────────────────────────────────────
@found_person_bp.route("/found-report/<int:match_id>/validate", methods=["POST"])
@jwt_required()
def validate_found_match(match_id: int):
    current_identity = get_jwt_identity()
    uploader_id = current_identity.get("id")
    role = current_identity.get("role")
    owner_col = _owner_col(role)

    body = request.get_json(silent=True) or {}
    decision = (body.get("decision") or "").strip()

    if decision not in ("confirmed", "rejected"):
        return _err("decision must be 'confirmed' or 'rejected'.")

    status_val = "match" if decision == "confirmed" else "no_match"

    cur = None
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cur.execute(
            f"""
            SELECT mr.match_id, mr.missing_id, mr.found_id
            FROM match_results mr
            JOIN found_persons fp ON mr.found_id = fp.found_id
            WHERE mr.match_id      = %s
              AND fp.{owner_col}   = %s
              AND mr.status        = 'uncertain'
            """,
            (match_id, uploader_id),
        )
        row = cur.fetchone()
        if not row:
            return _err("Match not found, already resolved, or access denied.", 404)

        cur.execute(
            "UPDATE match_results SET status = %s WHERE match_id = %s",
            (status_val, match_id),
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
    return _ok(status_val, {
        "match_id": match_id,
    }, msg)