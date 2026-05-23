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
            image_path,
            sanitize_value(fields.get("phone_number1"), "phone"),
            sanitize_value(fields.get("phone_number2"), "phone"),
        )
    )
    new_id = cur.lastrowid
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
        image_path = save_image(image_file, category="found")

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
    # MATCH (>= 0.677)
    # ------------------------------------------------------------------
    if distances is not None and distances[0][0] >= MATCH_THRESHOLD:
        similarity     = float(distances[0][0])
        faiss_id       = int(indices[0][0])
        matched_person = get_missing_person_by_faiss_id(mysql, faiss_id)

        if matched_person:
            cur = None
            try:
                cur = mysql.connection.cursor()

                new_faiss_id  = add_embedding_to_index(embedding, category="found")
                new_found_id  = _insert_found_person(cur, organization_id, fields, image_path)

                cur.execute(
                    "UPDATE found_persons SET faiss_id = %s WHERE found_id = %s",
                    (new_faiss_id, new_found_id)
                )
                cur.execute(
                    """
                    INSERT INTO match_results
                        (missing_id, found_id, organization_id, similarity_score, status)
                    VALUES (%s, %s, %s, %s, 'confirmed')
                    """,
                    (matched_person.get("missing_id"), new_found_id, organization_id, similarity)
                )
                mysql.connection.commit()

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
    # UNCERTAIN (0.60 - 0.677)
    # ✅ لا نحفظ في DB - نرجع كل البيانات للـ frontend ويقرر المستخدم
    # ------------------------------------------------------------------
    if distances is not None and UNCERTAIN_THRESHOLD <= distances[0][0] < MATCH_THRESHOLD:
        similarity = float(distances[0][0])
        faiss_id   = int(indices[0][0])
        candidate  = get_missing_person_by_faiss_id(mysql, faiss_id)

        if candidate:
            return jsonify({
                "success":    True,
                "status":     "uncertain",
                # ✅ missing_id الموجود في DB أصلاً - الـ frontend يحتفظ بيه ويبعته في validate
                "matchId":    candidate.get("missing_id"),
                "percentage": round(similarity, 4),
                "details":    attach_image_url(candidate),
                # ✅ كل بيانات الفورم ترجع للـ frontend عشان يبعتها في validate
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

        new_faiss_id = add_embedding_to_index(embedding, category="found")
        new_found_id = _insert_found_person(cur, organization_id, fields, image_path)

        cur.execute(
            "UPDATE found_persons SET faiss_id = %s WHERE found_id = %s",
            (new_faiss_id, new_found_id)
        )
        mysql.connection.commit()

        return jsonify({
            "success":   True,
            "status":    "no_match",
            "found_id":  new_found_id,
            "image_url": build_image_url(image_path)
        }), 201

    except Exception:
        if cur: mysql.connection.rollback()
        traceback.print_exc()
        return jsonify({"success": False, "message": "Database error."}), 500
    finally:
        if cur: cur.close()


@found_person_bp.route("/report/<int:matchId>/validate", methods=["POST"])
@jwt_required()
def validate_found_match(matchId):
    """
    matchId  = missing_id (من الـ URL - نفس الـ matchId اللي رجع من uncertain)
    الـ body بيبعت:
      - decision:    "confirmed" | "rejected"
      - percentage:  similarity score
      - formData:    كل بيانات الفورم اللي رجعت من uncertain response
    """
    organization_id = 5
    body       = request.get_json(silent=True) or {}
    decision   = body.get("decision")
    similarity = body.get("percentage", 0)
    form_data  = body.get("formData")  # ✅ البيانات اللي رجعت من uncertain
    if not form_data:
        return jsonify({"success": False, "message": "formData مطلوب"}), 400

    image_path = form_data.get("image_path")
    if not image_path:
        return jsonify({"success": False, "message": "image_path مطلوب في formData"}), 400

    status_val = "match" if decision == "confirmed" else "no_match"

    cur = None
    try:
        cur = mysql.connection.cursor()

        # ✅ استخرج الـ embedding من الصورة المحفوظة مسبقاً
        embedding = extract_embedding(image_path)
        if embedding is None:
            return jsonify({"success": False, "message": "فشل استخراج الوجه من الصورة"}), 422

        # ✅ أضف للـ FAISS وخذ الـ faiss_id
        new_faiss_id = add_embedding_to_index(embedding, category="found")

        # ✅ احفظ في DB الآن بعد قرار المستخدم
        new_found_id = _insert_found_person(cur, organization_id, form_data, image_path)

        # ✅ ربط faiss_id
        cur.execute(
            "UPDATE found_persons SET faiss_id = %s WHERE found_id = %s",
            (new_faiss_id, new_found_id)
        )

        # ✅ سجل في match_results - matchId هو missing_id الموجود في DB
        cur.execute(
            """
            INSERT INTO match_results
                (missing_id, found_id, organization_id, similarity_score, status)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (matchId, new_found_id, organization_id, similarity, status_val)
        )
        mysql.connection.commit()

        msg = "تم تأكيد المطابقة" if decision == "confirmed" else "تم رفض المطابقة وحفظه كبلاغ جديد"
        return jsonify({
            "success":  True,
            "message":  msg,
            "status":   status_val,
            "found_id": 14
        }), 200

    except Exception as e:
        if mysql.connection: mysql.connection.rollback()
        print(f"[ERROR] validate_found_match: {e}")
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if cur: cur.close()
