from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import mysql
import MySQLdb.cursors
from ..services.face_service import delete_embedding_from_index, delete_image_safe 

missing_db_bp = Blueprint("missing_database", __name__)


def _require_admin(current_user):
    if current_user.get("role") != "admin":
        return jsonify({"message": "غير مصرح لك بهذا الإجراء"}), 403
    return None

def _require_admin_OR_authority(current_user):
    if current_user.get("role") not in ["admin", "authority"]:
        return jsonify({"message": "غير مصرح لك بهذا الإجراء"}), 403
    return None

@missing_db_bp.route("/missing-database", methods=["GET"])
@jwt_required()
def get_missing_database():
    current_user = get_jwt_identity()
    err = _require_admin_OR_authority(current_user)
    if err:
        return err

    try:
        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT
                mp.missing_id   AS id,
                mp.full_name,
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
                      AND status IN ('match', 'uncertain')
                    ORDER BY similarity_score DESC
                    LIMIT 1
                )
            ORDER BY mp.created_at DESC
        """)

        rows = cur.fetchall()
        cur.close()

        results = []
        for row in rows:
            missing_id, full_name, image_path, match_id, match_status = row

            if match_status == "match":
                frontend_status = "match"
            elif match_status == "uncertain":
                frontend_status = "uncertain"
            else:
                frontend_status = "nomatch"

            entry = {
                "id":         missing_id,
                "full_name":  full_name,
                "image_path": image_path,
                "status":     frontend_status,
            }

            if match_id and match_status in ("match", "uncertain"):
                entry["matchId"] = match_id

            results.append(entry)

        return jsonify(results), 200

    except Exception as e:
        return jsonify({"message": "فشل جلب قاعدة بيانات المفقودين", "error": str(e)}), 500


@missing_db_bp.route("/missing-database/<int:missing_id>", methods=["GET"])
@jwt_required()
def get_missing_by_id(missing_id):
    current_user = get_jwt_identity()
    err = _require_admin_OR_authority(current_user)
    if err:
        return err

    try:
        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT
                missing_id,
                full_name,
                age,
                gender,
                last_seen_date,
                last_seen_location,
                phone_number1,
                phone_number2,
                image_path
            FROM missing_persons
            WHERE missing_id = %s
        """, (missing_id,))

        row = cur.fetchone()
        cur.close()

        if not row:
            return jsonify({"message": "المفقود غير موجود"}), 404

        (
            missing_id, full_name, age, gender,
            last_seen_date, last_seen_location,
            phone_number1, phone_number2, image_path
        ) = row

        return jsonify({
            "id":                 missing_id,
            "full_name":          full_name,
            "age":                age,
            "gender":             gender,
            "last_seen_date":     str(last_seen_date) if last_seen_date else None,
            "last_seen_location": last_seen_location,
            "phone_number1":      phone_number1,
            "phone_number2":      phone_number2,
            "image_path":         image_path,
        }), 200

    except Exception as e:
        return jsonify({"message": "فشل جلب بيانات المفقود", "error": str(e)}), 500


@missing_db_bp.route("/missing-database/<int:missing_id>", methods=["DELETE"])
@jwt_required()
def delete_missing(missing_id):
    current_user = get_jwt_identity()
    err = _require_admin(current_user)
    if err:
        return err

    try:
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # ← DictCursor

        cur.execute(
            "SELECT missing_id, faiss_id, image_path FROM missing_persons WHERE missing_id = %s",
            (missing_id,)
        )
        row = cur.fetchone()
        if not row:
            cur.close()
            return jsonify({"message": "المفقود غير موجود"}), 404

        faiss_id = row["faiss_id"] 
        image_path = row["image_path"]

        cur.execute("DELETE FROM missing_persons WHERE missing_id = %s", (missing_id,))
        mysql.connection.commit()
        cur.close()

    except Exception as e:
        return jsonify({"message": "فشل حذف البلاغ", "error": str(e)}), 500

    if faiss_id is not None:
        delete_embedding_from_index(faiss_id, category="missing")
    if image_path:
        delete_image_safe(image_path)

    return jsonify({"message": "تم حذف البلاغ بنجاح"}), 200



@missing_db_bp.route("/missing-database-match/<int:match_id>", methods=["GET"])
@jwt_required()
def get_match_details(match_id):
    current_user = get_jwt_identity()
    err = _require_admin_OR_authority(current_user)
    if err:
        return err

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
            LEFT JOIN authority a
                ON a.authority_id = fp.authority_id
            LEFT JOIN users u
                ON u.user_id = fp.uploaded_by_admin_id
            WHERE mr.match_id = %s
        """, (match_id,))

        row = cur.fetchone()
        cur.close()

        if not row:
            return jsonify({"message": "التطابق غير موجود"}), 404

        (
            similarity_score, full_name, approximate_age, gender,
            health_status, found_date, found_location, image_path,
            phone_number1, phone_number2, authority_name, uploaded_by_type
        ) = row

        return jsonify({
            "percentage":       round(float(similarity_score), 4),
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
        return jsonify({"message": "فشل جلب تفاصيل التطابق", "error": str(e)}), 500



@missing_db_bp.route("/missing-database-match/<int:match_id>/cancel", methods=["PATCH"])
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
