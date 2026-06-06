from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import MySQLdb.cursors
from ..extensions import mysql
from ..services.face_service import sanitize_value, delete_embedding_from_index  # ← added

my_missing_bp = Blueprint("my_missing", __name__)

ALLOWED_FIELDS = {
    "full_name", "age", "gender",
    "last_seen_location", "last_seen_date",
    "phone_number1", "phone_number2"
}

REQUIRED_IF_SENT = {"full_name", "phone_number1", "phone_number2"}


@my_missing_bp.route("/my-missing-cases", methods=["GET"])
@jwt_required()
def get_my_missing_cases():
    current_user = get_jwt_identity()
    user_id = current_user.get("id")

    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT
                mp.missing_id AS id,
                mp.full_name,
                mp.age,
                mp.gender,
                mp.last_seen_date,
                mp.last_seen_location,
                mp.phone_number1,
                mp.phone_number2,
                mp.image_path,
                mr.match_id AS match_id,
                mr.status AS match_status
            FROM missing_persons mp
            LEFT JOIN match_results mr
                ON mr.missing_id = mp.missing_id
                AND mr.match_id = (
                    SELECT match_id
                    FROM match_results
                    WHERE missing_id = mp.missing_id
                      AND status = 'match'
                    ORDER BY similarity_score DESC
                    LIMIT 1
                )
            WHERE mp.user_id = %s
            ORDER BY mp.created_at DESC
        """, (user_id,))

        rows = cur.fetchall()
        cur.close()

        results = []
        for row in rows:
            (
                missing_id, full_name, age, gender,
                last_seen_date, last_seen_location,
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
                "id": missing_id,
                "full_name": full_name,
                "age": age,
                "gender": gender,
                "last_seen_date": str(last_seen_date) if last_seen_date else None,
                "last_seen_location": last_seen_location,
                "phone_number1": phone_number1,
                "phone_number2": phone_number2,
                "image_path": image_path,
                "status": frontend_status,
            }

            if match_id and match_status in ("match", "uncertain"):
                entry["matchId"] = match_id

            results.append(entry)

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"message": "فشل جلب البلاغات", "error": str(e)}), 500


@my_missing_bp.route("/my-missing-cases/<int:missing_id>", methods=["DELETE"])
@jwt_required()
def delete_missing_case(missing_id):
    current_user = get_jwt_identity()
    user_id = current_user.get("id")

    try:
        #explain what does this do why do we need db???
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # ← DictCursor to fetch faiss_id

        cur.execute(
            "SELECT missing_id, faiss_id FROM missing_persons WHERE missing_id = %s AND user_id = %s",
            (missing_id, user_id)
        )
        row = cur.fetchone()
        if not row:
            cur.close()
            return jsonify({"message": "البلاغ غير موجود أو لا تملك صلاحية حذفه"}), 404

        faiss_id = row["faiss_id"]  # ← grab before delete

        cur.execute("DELETE FROM missing_persons WHERE missing_id = %s", (missing_id,))
        mysql.connection.commit()
        cur.close()

    except Exception as e:
        return jsonify({"message": "فشل حذف البلاغ", "error": str(e)}), 500

    # After DB delete succeeds, clean up FAISS
    if faiss_id is not None:
        delete_embedding_from_index(faiss_id, category="missing")

    return jsonify({"message": "تم حذف البلاغ بنجاح"}), 200


@my_missing_bp.route("/my-missing-cases/<int:missing_id>", methods=["PUT"])
@jwt_required()
def update_missing_case(missing_id):
    current_user = get_jwt_identity()
    user_id = current_user.get("id")

    data = request.get_json()
    if not data:
        return jsonify({"message": "لا توجد بيانات للتحديث"}), 400

    incoming = {k: v for k, v in data.items() if k in ALLOWED_FIELDS}
    if not incoming:
        return jsonify({"message": "لا توجد حقول صالحة للتحديث"}), 400

    type_map = {
        "full_name": "str",
        "age": "int",
        "phone_number1": "phone",
        "phone_number2": "phone",
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
            "SELECT missing_id FROM missing_persons WHERE missing_id = %s AND user_id = %s",
            (missing_id, user_id)
        )
        if not cur.fetchone():
            cur.close()
            return jsonify({"message": "البلاغ غير موجود أو لا تملك صلاحية تعديله"}), 404

        set_clause = ", ".join(f"{col} = %s" for col in fields_to_update)
        values = list(fields_to_update.values()) + [missing_id]

        cur.execute(
            f"UPDATE missing_persons SET {set_clause} WHERE missing_id = %s",
            values
        )
        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "تم تحديث البلاغ بنجاح"}), 200

    except Exception as e:
        return jsonify({"message": "فشل تحديث البلاغ", "error": str(e)}), 500


@my_missing_bp.route("/my-missing-match/<int:match_id>", methods=["GET"])
@jwt_required()
def get_match_details(match_id):
    current_user = get_jwt_identity()
    user_id = current_user.get("id")

    try:
        cur = mysql.connection.cursor()
        cur.execute("""
        SELECT
            mr.similarity_score,
            fp.full_name,
            fp.approximate_age,
            fp.gender,
            fp.health_status,
            fp.found_date,
            fp.found_location,
            fp.image_path,
            fp.phone_number1,
            fp.phone_number2,
            COALESCE(
                a.authority_name,
                CONCAT(u.first_name, ' ', u.last_name)
            ) AS authority_name,
            CASE
                WHEN fp.authority_id IS NOT NULL THEN 'authority'
                WHEN fp.uploaded_by_admin_id IS NOT NULL THEN 'admin'
            END AS uploaded_by_type
        FROM match_results mr
        JOIN found_persons fp
            ON fp.found_id = mr.found_id
        JOIN missing_persons mp
            ON mp.missing_id = mr.missing_id
        LEFT JOIN authority a
            ON a.authority_id = fp.authority_id
        LEFT JOIN users u
            ON u.user_id = fp.uploaded_by_admin_id
        WHERE mr.match_id = %s
        AND mp.user_id = %s
        """, (match_id, user_id))

        row = cur.fetchone()
        cur.close()

        if not row:
            return jsonify({"message": "التطابق غير موجود أو لا تملك صلاحية الوصول إليه"}), 404

        (
            similarity_score, full_name, approximate_age, gender,
            health_status, found_date, found_location, image_path,
            phone_number1, phone_number2, authority_name, uploaded_by_type
        ) = row

        return jsonify({
            "percentage": round(float(similarity_score), 4),
            "full_name": full_name,
            "approximate_age": approximate_age,
            "gender": gender,
            "health_status": health_status,
            "found_date": str(found_date) if found_date else None,
            "found_location": found_location,
            "image_path": image_path,
            "phone_number1": phone_number1,
            "phone_number2": phone_number2,
            "authority_name": authority_name,
            "uploaded_by_type": uploaded_by_type,
        }), 200

    except Exception as e:
        return jsonify({"message": "فشل جلب تفاصيل التطابق", "error": str(e)}), 500