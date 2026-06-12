from __future__ import annotations
import logging
import MySQLdb.cursors
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from ..extensions import mysql
from ..services.face_service import (
    add_embedding_to_index,
    extract_embedding,
    get_found_person_by_faiss_id,
    sanitize_value,
    save_image,
    search_faiss_index,
    delete_image_safe,
)

logger = logging.getLogger(__name__)

missing_person_bp = Blueprint("missing_person", __name__)

MATCH_THRESHOLD = 0.677
UNCERTAIN_THRESHOLD = 0.60


# ===========================================================================
def _resp(success: bool, status: str, data: dict | None, message: str, http: int):
    response = {"status": status, "message": message}
    if data:
        response.update(data)
    return jsonify(response), http

def _ok(status: str, data: dict, message: str = ""):
    return _resp(True, status, data, message, 200)

def _created(status: str, data: dict, message: str = ""):
    return _resp(True, status, data, message, 201)

def _err(message: str, http: int = 400):
    return _resp(False, "error", None, message, http)


def _db_insert_missing(cur, user_id: int, fields: dict, image_path: str) -> int:
    cur.execute(
        """
        INSERT INTO missing_persons
            (user_id, full_name, age, gender,
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


# ===========================================================================
@missing_person_bp.route("/missing-report/send", methods=["POST"])
@jwt_required()
def send_missing_report():
    current_identity = get_jwt_identity()
    user_id = current_identity.get("id")

    required = ["full_name", "age", "gender", "phone_number1", "phone_number2"]
    missing  = [f for f in required if not (request.form.get(f) or "").strip()]
    if missing:
        return _err("يرجى إدخال جميع الحقول المطلوبة")

    image_file = request.files.get("image_path")
    if not image_file or not image_file.filename:
        return _err("يرجى إرفاق صورة للشخص المفقود")

    fields = {
        "full_name":          request.form["full_name"].strip(),
        "age":                request.form.get("age", "").strip(),
        "gender":             request.form["gender"].strip(),
        "last_seen_location": request.form.get("last_seen_location", "").strip(),
        "last_seen_date":     request.form.get("last_seen_date", "").strip(),
        "phone_number1":      (request.form.get("phone_number1") or "").strip(),
        "phone_number2":      (request.form.get("phone_number2") or "").strip(),
    }

    try:
        image_path: str = save_image(image_file, category="missing")
        embedding, rejection_reason = extract_embedding(image_path)
    except Exception:
        delete_image_safe(image_path)
        logger.exception("Image save/embedding failed")
        return _err("فشلت معالجة الصورة، يرجى المحاولة مرة أخرى", 500)

    if embedding is None:
        delete_image_safe(image_path)
        return _err(rejection_reason, 422)

    try:
        distances, indices = search_faiss_index(embedding, category="found", top_k=1)
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

    # ====================================== Match
    if is_match:
        matched = get_found_person_by_faiss_id(mysql, faiss_id)

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

                new_missing_id = _db_insert_missing(cur, user_id, fields, image_path)
                add_embedding_to_index(embedding, category="missing", faiss_id=new_missing_id)
                cur.execute(
                    "UPDATE missing_persons SET faiss_id = %s WHERE missing_id = %s",
                    (new_missing_id, new_missing_id),
                )

                match_result_id = _db_insert_match_result(
                    cur, new_missing_id, matched["found_id"], similarity, "match"
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
                "matchId":    match_result_id, 
                "percentage": round(similarity, 4),
                "details":    matched,
            }, "Match found.")

    # ====================================== uncertain
    if is_uncertain:
        candidate = get_found_person_by_faiss_id(mysql, faiss_id)

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

                new_missing_id = _db_insert_missing(cur, user_id, fields, image_path)
                add_embedding_to_index(embedding, category="missing", faiss_id=new_missing_id)
                cur.execute(
                    "UPDATE missing_persons SET faiss_id = %s WHERE missing_id = %s",
                    (new_missing_id, new_missing_id),
                )

                match_result_id = _db_insert_match_result(
                    cur, new_missing_id, candidate["found_id"], similarity, "uncertain"
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
                "missing_id": new_missing_id,
                "matchId":    match_result_id,   
                "percentage": round(similarity, 4),
                "details":    candidate,
            }, "Possible match found. Please validate.")

    # ====================================== no Match
    cur = None
    try:
        cur = mysql.connection.cursor()

        new_missing_id = _db_insert_missing(cur, user_id, fields, image_path)
        add_embedding_to_index(embedding, category="missing", faiss_id=new_missing_id)
        cur.execute(
            "UPDATE missing_persons SET faiss_id = %s WHERE missing_id = %s",
            (new_missing_id, new_missing_id),
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
    }, "Report submitted. No match found.")


@missing_person_bp.route("/report/<int:match_id>/validate", methods=["POST"])
@jwt_required()
def validate_match(match_id: int):
    current_identity = get_jwt_identity()
    user_id = current_identity.get("id")

    body = request.get_json(silent=True) or {}
    decision = (body.get("decision") or "").strip()

    if decision not in ("confirmed", "rejected"):
        return _err("decision must be 'confirmed' or 'rejected'.")

    status_val = "match" if decision == "confirmed" else "no_match"

    cur = None
    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cur.execute(
            """
            SELECT mr.match_id, mr.missing_id, mr.found_id
            FROM match_results mr
            JOIN missing_persons mp ON mr.missing_id = mp.missing_id
            WHERE mr.match_id = %s
              AND mp.user_id  = %s
              AND mr.status   = 'uncertain'
            """,
            (match_id, user_id),
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
        logger.exception("DB error — validate_match")
        return _err("Database error during validation.", 500)
    finally:
        if cur:
            cur.close()

    msg = "Match confirmed." if decision == "confirmed" else "Match rejected. Report saved independently."
    return _ok(status_val, {
        "match_id":   match_id,
    }, msg)