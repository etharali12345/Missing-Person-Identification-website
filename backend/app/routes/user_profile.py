from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash

from ..services.face_service import sanitize_value
from ..extensions import mysql

user_profile_bp = Blueprint("user_profile", __name__)


@user_profile_bp.route("/user-profile", methods=["GET"])
@jwt_required()
def get_user_profile():
    identity = get_jwt_identity()
    user_id = identity.get("id")

    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT first_name, last_name, email_or_phone FROM users WHERE user_id = %s",
        (user_id,),
    )
    user = cur.fetchone()
    cur.close()

    if not user:
        return jsonify({"error": "المستخدم غير موجود"}), 404

    return jsonify({
        "first_name":     user[0],
        "last_name":      user[1],
        "email_or_phone": user[2],
    }), 200


@user_profile_bp.route("/user-profile/info", methods=["PUT"])
@jwt_required()
def update_user_info():
    identity = get_jwt_identity()
    user_id = identity.get("id")

    data = request.get_json()
    if not data:
        return jsonify({"error": "لا توجد بيانات"}), 400

    first_name     = sanitize_value(data.get("first_name"))
    last_name      = sanitize_value(data.get("last_name"))
    email_or_phone = sanitize_value(data.get("email_or_phone"), expected_type="phone")

    if not first_name or not last_name or not email_or_phone:
        return jsonify({"error": "جميع الحقول مطلوبة"}), 400

    cur = mysql.connection.cursor()
    try:
        cur.execute(
            "UPDATE users SET first_name = %s, last_name = %s, email_or_phone = %s "
            "WHERE user_id = %s",
            (first_name, last_name, email_or_phone, user_id),
        )
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": "فشل تحديث البيانات", "details": str(e)}), 500
    finally:
        cur.close()

    return jsonify({"message": "تم تحديث البيانات بنجاح"}), 200


@user_profile_bp.route("/user-profile/password", methods=["PUT"])
@jwt_required()
def update_user_password():
    identity = get_jwt_identity()
    user_id = identity.get("id")

    data = request.get_json()
    if not data:
        return jsonify({"error": "لا توجد بيانات"}), 400

    old_password = sanitize_value(data.get("old_password"))
    new_password = sanitize_value(data.get("new_password"))

    if not old_password or not new_password:
        return jsonify({"error": "يرجى إدخال كلمة المرور القديمة والجديدة"}), 400


    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT password FROM users WHERE user_id = %s",
        (user_id,),
    )
    user = cur.fetchone()
    cur.close()

    if not user:
        return jsonify({"error": "المستخدم غير موجود"}), 404

    if not check_password_hash(user[0], old_password):
        return jsonify({"error": "كلمة المرور القديمة غير صحيحة"}), 401

    hashed = generate_password_hash(new_password)

    cur = mysql.connection.cursor()
    try:
        cur.execute(
            "UPDATE users SET password = %s WHERE user_id = %s",
            (hashed, user_id),
        )
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({"error": "فشل تحديث كلمة المرور", "details": str(e)}), 500
    finally:
        cur.close()

    return jsonify({"message": "تم تحديث كلمة المرور بنجاح"}), 200