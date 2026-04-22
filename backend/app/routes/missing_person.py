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
    get_user_id_by_identity,
    get_found_person_by_faiss_id,
    build_image_url,
    attach_image_url,
    sanitize_value,
)

missing_person_bp = Blueprint("missing_person", __name__)

MATCH_THRESHOLD     = 0.677
UNCERTAIN_THRESHOLD = 0.60


def _insert_missing_person(cur, user_id, fields, image_path):
    """
    Helper مركزي لإدخال missing_person - يضمن تنظيف البيانات دايماً.
    ✅ faiss_id يتحدد من برا الـ function عبر add_embedding_to_index
    """
    if hasattr(image_path, 'filename'):
        raise ValueError("image_path must be a string path, not FileStorage object")

    # ✅ INSERT بدون faiss_id - هيتحدث بعدين
    cur.execute(
        """
        INSERT INTO missing_persons
            (user_id, full_name, approximate_age, gender,
             last_seen_location, last_seen_date, phone_number1, phone_number2, image_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            user_id,
            sanitize_value(fields.get("full_name", "Unknown")),
            sanitize_value(fields.get("age"), "int"),
            sanitize_value(fields.get("gender")),
            sanitize_value(fields.get("last_seen_location")),
            sanitize_value(fields.get("last_seen_date")),
            sanitize_value(fields.get("phone_number1"), "phone"),
            sanitize_value(fields.get("phone_number2"), "phone"),
            image_path,
        )
    )
    new_id = cur.lastrowid
    return new_id


@missing_person_bp.route("/missing-report/send", methods=["POST"])
@jwt_required()
def send_missing_report():
    user_id = 6

    required_fields = ["full_name", "age", "gender", "phone_number1", "phone_number2"]
    missing_fields  = [f for f in required_fields if not request.form.get(f)]
    if missing_fields:
        return jsonify({"success": False, "message": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    image_file = request.files.get("image_path")
    if not image_file or image_file.filename == "":
        return jsonify({"success": False, "message": "Image file is required."}), 400

    fields = {
        "full_name":          request.form["full_name"].strip(),
        "age":                request.form.get("age", "").strip(),
        "gender":             request.form["gender"].strip(),
        "last_seen_location": request.form.get("last_seen_location", "").strip(),
        "last_seen_date":     request.form.get("last_seen_date", "").strip(),
        "phone_number1":      request.form.get("phone_number1").strip(),
        "phone_number2":      request.form.get("phone_number2").strip(),
    }

    try:
        saved_image_path = save_image(image_file, category="missing")

        if not isinstance(saved_image_path, str):
            raise ValueError(f"save_image returned non-string: {type(saved_image_path)}")

        embedding = extract_embedding(saved_image_path)
        if embedding is None:
            return jsonify({"success": False, "message": "No face detected."}), 422

        distances, indices = search_faiss_index(embedding, category="found", top_k=1)
    except Exception:
        traceback.print_exc()
        return jsonify({"success": False, "message": "Internal error during processing."}), 500

    # ------------------------------------------------------------------
    # MATCH (>= 0.677)
    # ------------------------------------------------------------------
    if distances is not None and distances[0][0] >= MATCH_THRESHOLD:
        similarity = float(distances[0][0])
        faiss_id   = int(indices[0][0])                                      # ✅ اسم واضح
        matched_person = get_found_person_by_faiss_id(mysql, faiss_id)       # ✅ نفس المتغير

        if matched_person:
            cur = None
            try:
                cur = mysql.connection.cursor()

                # ✅ 1) أضف للـ FAISS الأول عشان تاخد faiss_id صحيح
                new_faiss_id = add_embedding_to_index(embedding, category="missing")

                # ✅ 2) احفظ في DB
                new_missing_id = _insert_missing_person(cur, user_id, fields, saved_image_path)

                # ✅ 3) ربط faiss_id بالـ missing_person
                cur.execute(
                    "UPDATE missing_persons SET faiss_id = %s WHERE missing_id = %s",
                    (new_faiss_id, new_missing_id)
                )

                cur.execute(
                    """
                    INSERT INTO match_results
                        (missing_id, found_id, user_id, similarity_score, status)
                    VALUES (%s, %s, %s, %s, 'confirmed')
                    """,
                    (new_missing_id, matched_person.get("found_id"), user_id, similarity)
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
                "matchId":    matched_person.get("found_id"),
                "percentage": round(similarity, 4),
                "details":    attach_image_url(matched_person)
            }), 200

    # ------------------------------------------------------------------
    # UNCERTAIN (0.60 - 0.677) - احفظ missing_person في DB وانتظر قرار المستخدم
    # ------------------------------------------------------------------
    if distances is not None and UNCERTAIN_THRESHOLD <= distances[0][0] < MATCH_THRESHOLD:
        similarity = float(distances[0][0])
        faiss_id   = int(indices[0][0])
        candidate  = get_found_person_by_faiss_id(mysql, faiss_id)

        if candidate:
            cur = None
            try:
                cur = mysql.connection.cursor()
                # ✅ احفظ في DB وانتظر قرار المستخدم - مش بنضيف للـ FAISS لسه
                new_missing_id = _insert_missing_person(cur, user_id, fields, saved_image_path)
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
                "matchId":    candidate.get("found_id"),
                "missing_id": new_missing_id,
                "percentage": round(similarity, 4),
                "details":    attach_image_url(candidate),
                "image_url":  build_image_url(saved_image_path)
            }), 200

    # ------------------------------------------------------------------
    # NO MATCH - احفظ في missing_persons وأضف للـ FAISS
    # ------------------------------------------------------------------
    cur = None
    try:
        cur = mysql.connection.cursor()

        # ✅ 1) أضف للـ FAISS الأول
        new_faiss_id = add_embedding_to_index(embedding, category="missing")

        # ✅ 2) احفظ في DB
        new_missing_id = _insert_missing_person(cur, user_id, fields, saved_image_path)

        # ✅ 3) ربط faiss_id بالـ missing_person
        cur.execute(
            "UPDATE missing_persons SET faiss_id = %s WHERE missing_id = %s",
            (new_faiss_id, new_missing_id)
        )

        mysql.connection.commit()

        return jsonify({
            "success":    True,
            "status":     "no_match",
            "missing_id": new_missing_id,
            "image_url":  build_image_url(saved_image_path)
        }), 201

    except Exception:
        if cur: mysql.connection.rollback()
        traceback.print_exc()
        return jsonify({"success": False, "message": "Database error."}), 500
    finally:
        if cur: cur.close()


@missing_person_bp.route("/report/<int:matchId>/validate", methods=["POST"])
@jwt_required()
def validate_match(matchId):
    """
    matchId  = found_id (من الـ URL - بيجي من الـ frontend زي ما كان)
    الـ body بيبعت:
      - decision:    "confirmed" | "rejected"
      - percentage:  similarity score
      - missing_id:  الـ ID اللي رجع من uncertain response
    """
    user_id    = 6
    body       = request.get_json(silent=True) or {}
    decision   = body.get("decision")
    similarity = body.get("percentage", 0)
    missing_id = body.get("missing_id")  # ✅ الـ frontend لازم يبعته من الـ uncertain response

    if not missing_id:
        return jsonify({"success": False, "message": "missing_id مطلوب - تأكد إن الـ frontend بيبعته"}), 400

    status_val = "match" if decision == "confirmed" else "no_match"

    cur = None
    try:
        cur = mysql.connection.cursor()

        # ✅ تحقق إن missing_id موجود وجيب image_path منه
        cur.execute("SELECT missing_id, image_path FROM missing_persons WHERE missing_id = %s", (missing_id,))
        row = cur.fetchone()
        if not row:
            return jsonify({"success": False, "message": f"missing_id {missing_id} غير موجود"}), 404

        # ✅ أضف للـ FAISS وربط faiss_id (في الحالتين confirmed و rejected)
        image_path = row[1] if isinstance(row, tuple) else row.get("image_path", "")
        embedding  = extract_embedding(image_path) if image_path else None

        if embedding is not None:
            new_faiss_id = add_embedding_to_index(embedding, category="missing")
            cur.execute(
                "UPDATE missing_persons SET faiss_id = %s WHERE missing_id = %s",
                (new_faiss_id, missing_id)
            )

        # ✅ سجل في match_results - matchId هو found_id
        cur.execute(
            """
            INSERT INTO match_results
                (missing_id, found_id, user_id, similarity_score, status)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (missing_id, matchId, user_id, similarity, status_val)
        )
        mysql.connection.commit()

        msg = "تم تأكيد المطابقة" if decision == "confirmed" else "تم رفض المطابقة وحفظه كبلاغ جديد"
        return jsonify({
            "success": True,
            "message": msg,
            "status":  status_val
        }), 200

    except Exception as e:
        print(f"[ERROR] validate_match: {e}")
        traceback.print_exc()
        if mysql.connection: mysql.connection.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        if cur: cur.close()