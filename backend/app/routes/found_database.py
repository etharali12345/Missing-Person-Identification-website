from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import mysql

found_db_bp = Blueprint("found_database", __name__)


def _require_admin(current_user):
    if current_user.get("role") != "admin":
        return jsonify({"message": "غير مصرح لك بهذا الإجراء"}), 403
    return None


@found_db_bp.route("/found-database", methods=["GET"])
@jwt_required()
def get_found_database():
    current_user = get_jwt_identity()
    err = _require_admin(current_user)
    if err:
        return err

    try:
        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT
                fp.found_id     AS id,
                fp.full_name,
                fp.image_path,
                mr.match_id     AS match_id,
                mr.status       AS match_status
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
            ORDER BY fp.created_at DESC
        """)

        rows = cur.fetchall()
        cur.close()

        results = []
        for row in rows:
            found_id, full_name, image_path, match_id, match_status = row

            entry = {
                "id":         found_id,
                "full_name":  full_name,
                "image_path": image_path,
                "status":     "match" if match_status == "match" else "nomatch",
            }

            if match_id and match_status == "match":
                entry["matchId"] = match_id

            results.append(entry)

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"message": "فشل جلب قاعدة بيانات المعثور عليهم", "error": str(e)}), 500


@found_db_bp.route("/found-database/<int:found_id>", methods=["GET"])
@jwt_required()
def get_found_by_id(found_id):
    current_user = get_jwt_identity()
    err = _require_admin(current_user)
    if err:
        return err

    try:
        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT
                fp.found_id,
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
            FROM found_persons fp
            LEFT JOIN authority a
                ON a.authority_id = fp.authority_id
            LEFT JOIN users u
                ON u.user_id = fp.uploaded_by_admin_id
            WHERE fp.found_id = %s
        """, (found_id,))

        row = cur.fetchone()
        cur.close()

        if not row:
            return jsonify({"message": "المعثور عليه غير موجود"}), 404

        (
            found_id, full_name, approximate_age, gender,
            health_status, found_date, found_location, image_path,
            phone_number1, phone_number2, authority_name, uploaded_by_type
        ) = row

        return jsonify({
            "id":               found_id,
            "full_name":        full_name,
            "approximate_age":  approximate_age,
            "gender":           gender,
            "health_status":    health_status,
            "found_date":       str(found_date) if found_date else None,
            "found_location":   found_location,
            "image_path":       image_path,
            "phone_number1":    phone_number1,
            "phone_number2":    phone_number2,
            "authority_name":   authority_name,
            "uploaded_by_type": uploaded_by_type,
        }), 200

    except Exception as e:
        return jsonify({"message": "فشل جلب بيانات المعثور عليه", "error": str(e)}), 500



@found_db_bp.route("/found-database/<int:found_id>", methods=["DELETE"])
@jwt_required()
def delete_found(found_id):
    current_user = get_jwt_identity()
    err = _require_admin(current_user)
    if err:
        return err

    try:
        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT found_id FROM found_persons WHERE found_id = %s",
            (found_id,)
        )
        if not cur.fetchone():
            cur.close()
            return jsonify({"message": "المعثور عليه غير موجود"}), 404

        cur.execute("DELETE FROM found_persons WHERE found_id = %s", (found_id,))
        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "تم حذف البلاغ بنجاح"}), 200

    except Exception as e:
        return jsonify({"message": "فشل حذف البلاغ", "error": str(e)}), 500



@found_db_bp.route("/found-database-match/<int:match_id>", methods=["GET"])
@jwt_required()
def get_match_details(match_id):
    current_user = get_jwt_identity()
    err = _require_admin(current_user)
    if err:
        return err

    try:
        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT
                mr.similarity_score,
                mp.full_name,
                mp.age,
                mp.gender,
                mp.last_seen_date,
                mp.last_seen_location,
                mp.image_path,
                mp.phone_number1,
                mp.phone_number2
            FROM match_results mr
            JOIN missing_persons mp
                ON mp.missing_id = mr.missing_id
            WHERE mr.match_id = %s
        """, (match_id,))

        row = cur.fetchone()
        cur.close()

        if not row:
            return jsonify({"message": "التطابق غير موجود"}), 404

        (
            similarity_score, full_name, age, gender,
            last_seen_date, last_seen_location, image_path,
            phone_number1, phone_number2
        ) = row

        return jsonify({
            "percentage":         round(float(similarity_score), 4),
            "full_name":          full_name,
            "age":                age,
            "gender":             gender,
            "last_seen_date":     str(last_seen_date) if last_seen_date else None,
            "last_seen_location": last_seen_location,
            "image_path":         image_path,
            "phone_number1":      phone_number1,
            "phone_number2":      phone_number2,
        }), 200

    except Exception as e:
        return jsonify({"message": "فشل جلب تفاصيل التطابق", "error": str(e)}), 500



@found_db_bp.route("/found-database-match/<int:match_id>/cancel", methods=["PATCH"])
@jwt_required()
def cancel_match(match_id):
    current_user = get_jwt_identity()
    err = _require_admin(current_user)
    if err:
        return err

    try:
        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT match_id FROM match_results WHERE match_id = %s",
            (match_id,)
        )
        if not cur.fetchone():
            cur.close()
            return jsonify({"message": "التطابق غير موجود"}), 404

        cur.execute(
            "UPDATE match_results SET status = 'no_match' WHERE match_id = %s",
            (match_id,)
        )
        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "تم إلغاء التطابق بنجاح"}), 200

    except Exception as e:
        return jsonify({"message": "فشل إلغاء التطابق", "error": str(e)}), 500