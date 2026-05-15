
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash,check_password_hash
from flask_jwt_extended import create_access_token,jwt_required, get_jwt_identity, set_access_cookies,unset_jwt_cookies

from ..extensions import mysql
import os

auth_bp = Blueprint("auth", __name__)



@auth_bp.route("/signup", methods=["POST"])
def signup():
    try:
        # الحالة الأولى: تسجيل مستخدم عادي (JSON)
        if request.is_json:
            data = request.get_json()
            role = data.get("role")

            if role != "user":
                return jsonify({"message": "Invalid role for this endpoint"}), 400

            hashed_password = generate_password_hash(data["password"])

            # إدخال البيانات في جدول users
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO users (first_name, last_name, email_or_phone, password)
                VALUES (%s, %s, %s, %s)
            """, (
                data["first_name"],
                data["last_name"],
                data["email_or_phone"],
                hashed_password
            ))
            mysql.connection.commit()
            cur.close()

            # إنشاء التوكن (Identity تحتوي على الإيميل والـ Role)
            access_token = create_access_token(identity={
                "email": data["email_or_phone"],
                "role": "user"
            })

            # تجهيز الرد وإرسال الكوكيز
            response = jsonify({
                "message": "User created successfully",
                "role": "user",
                "user": {
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "email": data["email_or_phone"]
                }
            })
            set_access_cookies(response, access_token)
            return response, 201

        #  الحالة الثانية: تسجيل جهة رسمية 
        else:
            role = request.form.get("role")
            if role != "authority":
                return jsonify({"message": "Invalid role"}), 400

            # استلام البيانات من الـ Form
            auth_type = request.form.get("authority_type")
            auth_name = request.form.get("authority_name")
            email_or_phone = request.form.get("email_or_phone")
            password = generate_password_hash(request.form.get("password"))
            location = request.form.get("location")
            license_num = request.form.get("license_number")

            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO authority (authority_type, authority_name, email_or_phone, password, location, license_number, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (auth_type, auth_name, email_or_phone, password, location, license_num, 'pending'))
            
            mysql.connection.commit()
            cur.close()
            access_token = create_access_token(identity={
                "email": email_or_phone,
                "role": "authority"
            })

            response = jsonify({
                "message": "Authority request submitted successfully (Pending Approval)",
                "role": "authority"
            })
            set_access_cookies(response, access_token)
            return response, 201

    except Exception as e:
        return jsonify({"message": "Internal Server Error", "error": str(e)}), 500
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email_or_phone = data.get("email_or_phone")
        password = data.get("password")
        cur = mysql.connection.cursor()
        
        # البحث في جدول المستخدمين (users)
        cur.execute("SELECT * FROM users WHERE email_or_phone = %s", (email_or_phone,))
        user = cur.fetchone()

        if user and check_password_hash(user[4], password):
            cur.close()
            access_token = create_access_token(identity={"email": user[3], "role": "user"})
            
            response = jsonify({
                "message": "Login successful",
                "role": "user",
                "user": {'role':'user'}
            })
            set_access_cookies(response, access_token)
            return response, 200

        #  البحث في جدول الجهات (authority) إذا لم يجد في الأول
        cur.execute("SELECT * FROM authority WHERE email_or_phone = %s", (email_or_phone,))
        auth_user = cur.fetchone()
        cur.close()

        if auth_user and check_password_hash(auth_user[5], password):
            access_token = create_access_token(identity={"email": auth_user[4], "role": "authority"})
            
            response = jsonify({
                "message": "Login successful",
                "user": {
                    "role": "authority"
                    }
            })
            set_access_cookies(response, access_token)
            return response, 200
        
        #  فشل تسجيل الدخول
        return jsonify({"message": "Invalid email/phone or password"}), 401

    except Exception as e:
        return jsonify({"message": "Internal Server Error", "error": str(e)}), 500
    
#الدالة اللي بترجع لي المستخدم الحالي للنظام 
@auth_bp.route("/me", methods=["GET"])
@jwt_required() 
def get_current_user():
    try:
        # استخراج البيانات المخزنة داخل التوكن (Email و Role)
        current_identity = get_jwt_identity()
        email = current_identity.get("email")
        role = current_identity.get("role")

        cur = mysql.connection.cursor()

        #  لو المستخدم عادي
        if role == "user":
            cur.execute("SELECT first_name, last_name, email_or_phone FROM users WHERE email_or_phone = %s", (email,))
            user = cur.fetchone()
            cur.close()
            if user:
                return jsonify({
                    "user": {
                        "role": "user"
                    }
                }), 200

        #  لو المستخدم جهة رسمية (Authority)
        elif role == "authority":
            cur.execute("SELECT authority_type, authority_name, email_or_phone FROM authority WHERE email_or_phone = %s", (email,))
            auth_user = cur.fetchone()
            cur.close()
            if auth_user:
                return jsonify({
                    "user": {
                        "role": "authority"
                    }
                }), 200

        return jsonify({"message": "User not found"}), 404

    except Exception as e:
        return jsonify({"message": "Server error"}), 500
    
#روات تسجيل الخروج 
@auth_bp.route("/logout", methods=["POST"])
def logout():
    resp = jsonify({"message": "Successfully logged out"})
    unset_jwt_cookies(resp)
    return resp, 200

