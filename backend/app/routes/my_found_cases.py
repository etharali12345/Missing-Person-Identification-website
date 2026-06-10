from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import MySQLdb.cursors
from ..extensions import mysql
from ..services.face_service import sanitize_value, delete_embedding_from_index  # ← added

my_found_bp = Blueprint("my_found", __name__)

ALLOWED_FIELDS = {
    "full_name", "approximate_age", "gender",
    "found_location", "found_date",
    "health_status", "phone_number1", "phone_number2"
}

REQUIRED_IF_SENT = {"phone_number1", "phone_number2"}

def _owner_col(role):
    return "uploaded_by_admin_id" if role == "admin" else "authority_id"


@my_found_bp.route("/my-found-cases", methods=["GET"])
@jwt_required()
def get_my_found_cases():
    current_user = get_jwt_identity()
    uploader_id = current_user.get("id")
    role = current_user.get("role")
    owner_col = _owner_col(role)

    try:
        cur = mysql.connection.cursor()

        cur.execute(f"""
            SELECT
                fp.found_id AS id,
                fp.full_name,
                fp.approximate_age,
                fp.gender,
                fp.found_date,
                fp.found_location,
                fp.health_status,
                fp.phone_number1,
                fp.phone_number2,
                fp.image_path,
                mr.match_id AS match_id,
                mr.status AS match_status
            FROM found_persons fp
            LEFT JOIN match_results mr
                ON mr.found_id = fp.found_id
                AND mr.match_id = (
                    SELECT match_id
                    FROM match_results
                    WHERE found_id = fp.found_id
                      AND status = 'match'
                    ORDER BY similarity_score DESC
                    LIMIT 1
                )
            WHERE fp.{owner_col} = %s
            ORDER BY fp.created_at DESC
        """, (uploader_id,))

        rows = cur.fetchall()
        cur.close()

        results = []
        for row in rows:
            (
                found_id, full_name, approximate_age, gender,
                found_date, found_location, health_status,
                phone_number1, phone_number2, image_path,
                match_id, match_status
            ) = row

            if match_status == "match":
                frontend_status = "match"
            elif match_status == "uncertain":
                frontend_status = "uncertain"
            else:
                frontend_status = "nomatch"

            entry = {
                "id": found_id,
                "full_name": full_name,
                "approximate_age": approximate_age,
                "gender": gender,
                "found_date": str(found_date) if found_date else None,
                "found_location": found_location,
                "health_status": health_status,
                "phone_number1": phone_number1,
                "phone_number2": phone_number2,
                "image_path": image_path,
                "status": frontend_status,
            }

            if match_id and match_status == "match":
                entry["matchId"] = match_id

            results.append(entry)

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"message": "فشل جلب البلاغات", "error": str(e)}), 500


@my_found_bp.route("/my-found-cases/<int:found_id>", methods=["DELETE"])
@jwt_required()
def delete_found_case(found_id):
    current_user = get_jwt_identity()
    uploader_id = current_user.get("id")
    role = current_user.get("role")
    owner_col = _owner_col(role)

    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 

        cur.execute(
            f"SELECT found_id, faiss_id FROM found_persons WHERE found_id = %s AND {owner_col} = %s",
            (found_id, uploader_id)
        )
        row = cur.fetchone()
        if not row:
            cur.close()
            return jsonify({"message": "البلاغ غير موجود أو لا تملك صلاحية حذفه"}), 404

        faiss_id = row["faiss_id"] 

        cur.execute("DELETE FROM found_persons WHERE found_id = %s", (found_id,))
        mysql.connection.commit()
        cur.close()

    except Exception as e:
        return jsonify({"message": "فشل حذف البلاغ", "error": str(e)}), 500

    if faiss_id is not None:
        delete_embedding_from_index(faiss_id, category="found")

    return jsonify({"message": "تم حذف البلاغ بنجاح"}), 200


@my_found_bp.route("/my-found-cases/<int:found_id>", methods=["PUT"])
@jwt_required()
def update_found_case(found_id):
    current_user = get_jwt_identity()
    uploader_id = current_user.get("id")
    role = current_user.get("role")
    owner_col = _owner_col(role)

    data = request.get_json()
    if not data:
        return jsonify({"message": "لا توجد بيانات للتحديث"}), 400

    incoming = {k: v for k, v in data.items() if k in ALLOWED_FIELDS}
    if not incoming:
        return jsonify({"message": "لا توجد حقول صالحة للتحديث"}), 400

    type_map = {
        "full_name":      "str",
        "approximate_age": "int",
        "health_status":  "str",
        "phone_number1":  "phone",
        "phone_number2":  "phone",
    }
    fields_to_update = {}
    for field, raw_value in incoming.items():
        expected_type = type_map.get(field, "str")
        fields_to_update[field] = sanitize_value(raw_value, expected_type)

    missing_required = [
        f for f in REQUIRED_IF_SENT
        if f in fields_to_update and fields_to_update[f] is None
    ]

    if missing_required:
        return jsonify({
            "message": "الحقول التالية مطلوبة ولا يمكن أن تكون فارغة",
            "fields": missing_required
        }), 400

    try:
        cur = mysql.connection.cursor()

        cur.execute(
            f"SELECT found_id FROM found_persons WHERE found_id = %s AND {owner_col} = %s",
            (found_id, uploader_id)
        )
        if not cur.fetchone():
            cur.close()
            return jsonify({"message": "البلاغ غير موجود أو لا تملك صلاحية تعديله"}), 404

        set_clause = ", ".join(f"{col} = %s" for col in fields_to_update)
        values = list(fields_to_update.values()) + [found_id]

        cur.execute(
            f"UPDATE found_persons SET {set_clause} WHERE found_id = %s",
            values
        )
        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "تم تحديث البلاغ بنجاح"}), 200

    except Exception as e:
        return jsonify({"message": "فشل تحديث البلاغ", "error": str(e)}), 500


@my_found_bp.route("/found-match/<int:match_id>", methods=["GET"])
@jwt_required()
def get_match_details(match_id):
    current_user = get_jwt_identity()
    uploader_id = current_user.get("id")
    role = current_user.get("role")
    owner_col = _owner_col(role)

    try:
        cur = mysql.connection.cursor()

        cur.execute(f"""
            SELECT
                mr.similarity_score,
                mp.full_name,
                mp.age,
                mp.gender,
                mp.last_seen_date,
                mp.last_seen_location,
                mp.image_path,
                mp.phone_number1,
                mp.phone_number2,
                u.first_name,
                u.last_name,
                u.email_or_phone AS reporter_contact
            FROM match_results mr
            JOIN missing_persons mp
                ON mp.missing_id = mr.missing_id
            JOIN found_persons fp
                ON fp.found_id = mr.found_id
            JOIN users u
                ON u.user_id = mp.user_id
            WHERE mr.match_id = %s
              AND fp.{owner_col} = %s
        """, (match_id, uploader_id))

        row = cur.fetchone()
        cur.close()

        if not row:
            return jsonify({"message": "التطابق غير موجود أو لا تملك صلاحية الوصول إليه"}), 404

        (
            similarity_score, full_name, age, gender,
            last_seen_date, last_seen_location, image_path,
            phone_number1, phone_number2,
            first_name, last_name, reporter_contact
        ) = row

        return jsonify({
            "percentage": round(float(similarity_score), 4),
            "full_name": full_name,
            "age": age,
            "gender": gender,
            "last_seen_date": str(last_seen_date) if last_seen_date else None,
            "last_seen_location": last_seen_location,
            "image_path": image_path,
            "phone_number1": phone_number1,
            "phone_number2": phone_number2,
            "reporter_name": f"{first_name} {last_name}",
            "reporter_contact": reporter_contact,
        }), 200

    except Exception as e:
        return jsonify({"message": "فشل جلب تفاصيل التطابق", "error": str(e)}), 500


@my_found_bp.route("/found-match/<int:match_id>/cancel", methods=["PATCH"])
@jwt_required()
def cancel_match(match_id):
    current_user = get_jwt_identity()
    uploader_id = current_user.get("id")
    role = current_user.get("role")
    owner_col = _owner_col(role)

    try:
        cur = mysql.connection.cursor()

        cur.execute(f"""
            SELECT mr.match_id
            FROM match_results mr
            JOIN found_persons fp
                ON fp.found_id = mr.found_id
            WHERE mr.match_id = %s
              AND fp.{owner_col} = %s
        """, (match_id, uploader_id))

        if not cur.fetchone():
            cur.close()
            return jsonify({"message": "التطابق غير موجود أو لا تملك صلاحية إلغائه"}), 404

        cur.execute(
            "UPDATE match_results SET status = 'no_match' WHERE match_id = %s",
            (match_id,)
        )
        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "تم إلغاء التطابق بنجاح"}), 200

    except Exception as e:
        return jsonify({"message": "فشل إلغاء التطابق", "error": str(e)}), 500