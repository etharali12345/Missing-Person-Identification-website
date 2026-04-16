import traceback
import numpy as np
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import mysql

from app.services.face_service import (
    save_image,
    extract_embedding,
    search_faiss_index,
    add_embedding_to_index,
    get_authority_id_by_identity,
    get_missing_person_by_faiss_id,
    build_image_url,
    attach_image_url,
    sanitize_value,
)

found_person_bp = Blueprint("found_person", __name__)

MATCH_THRESHOLD     = 0.677
UNCERTAIN_THRESHOLD = 0.60


def _insert_found_person(cur, organization_id, fields, image_path):
    """
    Helper مركزي لإدخال found_person - يضمن تنظيف البيانات دايماً.
    """
    # ✅ تأكد إن image_path string مش FileStorage
    if hasattr(image_path, 'filename'):
        raise ValueError("image_path must be a string path, not FileStorage object")

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
            image_path,                                           # ✅ string مضمون
            sanitize_value(fields.get("phone_number1")),
            sanitize_value(fields.get("phone_number2")),
        )
    )
    new_id = cur.lastrowid
    cur.execute(
        "UPDATE found_persons SET faiss_id = %s WHERE found_id = %s",
        (new_id, new_id)
    )
    return new_id


@found_person_bp.route("/found-report/send", methods=["POST"])
@jwt_required()
def send_found_report():
    organization_id = 5

    required_fields = ["phone_number1", "phone_number2"]
    missing_fields  = [f for f in required_fields if not request.form.get(f)]
    if missing_fields:
        return jsonify({"success": False, "message": f"Missing fields: {', '.join(missing_fields)}"}), 400

    image_file = request.files.get("image_path")
    if not image_file:
        return jsonify({"success": False, "message": "Image file is required."}), 400

    # ✅ استخرج البيانات كـ strings نظيفة
    fields = {
        "full_name":       request.form.get("full_name", "Unknown").strip(),
        "approximate_age": request.form.get("approximate_age", "").strip(),
        "gender":          request.form.get("gender", "").strip(),
        "found_location":  request.form.get("found_location", "").strip(),
        "found_date":      request.form.get("found_date", "").strip(),
        "health_status":   request.form.get("health_status", "").strip(),
        "phone_number1":   request.form.get("phone_number1").strip(),
        "phone_number2":   request.form.get("phone_number2").strip(),
    }

    try:
        # ✅ save_image يرجع string path - مش FileStorage
        image_path = save_image(image_file, category="found")
        
        # ✅ تحقق إضافي
        if not isinstance(image_path, str):
            raise ValueError(f"save_image returned non-string: {type(image_path)}")

        embedding = extract_embedding(image_path)
        if embedding is None:
            return jsonify({"success": False, "message": "No face detected."}), 422

        distances, indices = search_faiss_index(embedding, category="missing", top_k=1)
    except Exception:
        traceback.print_exc()
        return jsonify({"success": False, "message": "Processing failed."}), 500

    # ------------------------------------------------------------------
    # MATCH (>= 0.677) - لا تحفظ found_person هنا، بس سجل في match_results
    # ------------------------------------------------------------------
    if distances is not None and distances[0][0] >= MATCH_THRESHOLD:
        similarity     = float(distances[0][0])
        faiss_row      = int(indices[0][0])
        matched_person = get_missing_person_by_faiss_id(mysql, faiss_row)

        if matched_person:
            cur = None
            try:
                cur = mysql.connection.cursor()

                # ✅ احفظ found_person أولاً عشان تاخد found_id حقيقي
                new_found_id = _insert_found_person(cur, organization_id, fields, image_path)

                cur.execute(
                    """
                    INSERT INTO match_results
                        (missing_id, found_id, organization_id, similarity_score, status)
                    VALUES (%s, %s, %s, %s, 'confirmed')
                    """,
                    (matched_person.get("missing_id"), new_found_id, organization_id, similarity)
                )
                mysql.connection.commit()
                add_embedding_to_index(embedding, category="found")

            except Exception:
                if cur: mysql.connection.rollback()
                traceback.print_exc()
                return jsonify({"success": False, "message": "Database error."}), 500
            finally:
                if cur: cur.close()

            return jsonify({
                "success":    True,
                "status":     "match",
                "matchId":    matched_person.get("missing_id"),
                "percentage": round(similarity, 4),
                "details":    attach_image_url(matched_person)
            }), 200

    # ------------------------------------------------------------------
    # UNCERTAIN (0.60 - 0.677) - احفظ found_person وانتظر قرار المستخدم
    # ------------------------------------------------------------------
    if distances is not None and UNCERTAIN_THRESHOLD <= distances[0][0] < MATCH_THRESHOLD:
        similarity = float(distances[0][0])
        faiss_row  = int(indices[0][0])
        candidate  = get_missing_person_by_faiss_id(mysql, faiss_row)

        if candidate:
            cur = None
            try:
                cur = mysql.connection.cursor()
                new_found_id = _insert_found_person(cur, organization_id, fields, image_path)
                mysql.connection.commit()
            except Exception:
                if cur: mysql.connection.rollback()
                traceback.print_exc()
                return jsonify({"success": False, "message": "Database error."}), 500
            finally:
                if cur: cur.close()

            return jsonify({
                "success":    True,
                "status":     "uncertain",
                "matchId":    candidate.get("missing_id"),
                "found_id":   new_found_id,
                "percentage": round(similarity, 4),
                "details":    attach_image_url(candidate),
                "formData": {
                    **fields,
                    "image_path": image_path,
                    "image_url":  build_image_url(image_path)
                }
            }), 200

    # ------------------------------------------------------------------
    # NO MATCH - احفظ في found_persons وأضف للـ FAISS
    # ------------------------------------------------------------------
    cur = None
    try:
        cur = mysql.connection.cursor()
        new_found_id = _insert_found_person(cur, organization_id, fields, image_path)
        mysql.connection.commit()
        add_embedding_to_index(embedding, category="found")

        return jsonify({
            "success":  True,
            "status":   "no_match",
            "found_id": new_found_id,
            "image_url": build_image_url(image_path)
        }), 201

    except Exception:
        if cur: mysql.connection.rollback()
        traceback.print_exc()
        return jsonify({"success": False, "message": "Database error."}), 500
    finally:
        if cur: cur.close()


@found_person_bp.route("/found-report/<int:matchId>/validate", methods=["POST"])
@jwt_required()
def validate_found_match(matchId):
    body       = request.get_json(silent=True) or {}
    decision   = body.get("decision")
    similarity = body.get("percentage", 0)
    found_id   = body.get("found_id")

    organization_id = 5
    cur = None
    try:
        cur = mysql.connection.cursor()

        if not found_id:
            return jsonify({"success": False, "message": "Missing found_id"}), 400

        # ✅ تحقق إن found_id موجود فعلاً في DB
        cur.execute("SELECT found_id FROM found_persons WHERE found_id = %s", (found_id,))
        if not cur.fetchone():
            return jsonify({"success": False, "message": f"found_id {found_id} not found"}), 404

        status_val = 'match' if decision == "confirmed" else 'no_match'

        cur.execute(
            """
            INSERT INTO match_results
                (missing_id, found_id, organization_id, similarity_score, status)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (matchId, found_id, organization_id, similarity, status_val)
        )
        mysql.connection.commit()
        return jsonify({"success": True, "message": "تمت العملية بنجاح"}), 200

    except Exception as e:
        if mysql.connection: mysql.connection.rollback()
        print(f"[ERROR] validate_found_match: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if cur: cur.close()