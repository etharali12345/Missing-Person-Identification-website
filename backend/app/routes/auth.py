from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
from ..extensions import mysql
import os

auth_bp = Blueprint("auth", __name__)



@auth_bp.route("/signup", methods=["POST"])
def signup():
    print("\n--- Incoming Signup Request ---")
    try:
        # 🟢 الحالة الأولى: بيانات JSON (User عادي)
        if request.is_json:
            data = request.get_json()
            print(f"Received JSON Data: {data}")

            # التأكد من الـ role أنه 'user'
            role = data.get("role")
            if role != "user": 
                print(f"⚠️ Validation Failed: Role is {role}, expected 'user'")
                return jsonify({"message": "Invalid role"}), 400

            hashed_password = generate_password_hash(data["password"])

            # تنفيذ الحفظ في قاعدة البيانات
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
            
            mysql.connection.commit() # السطر الأهم للحفظ في XAMPP
            cur.close()

            # إنشاء التوكن (Token)
            access_token = create_access_token(identity={
                "email": data["email_or_phone"], 
                "role": "user"
            })
            
            print("✅ Success: User saved and token generated!")

            # إرجاع الرد مع كائن الـ user والـ token والحالة 201
            return jsonify({
                "message": "User created successfully",
                "access_token": access_token,
                "user": {
                    "first_name": data["first_name"],
                    "last_name": data["last_name"],
                    "email": data["email_or_phone"],
                    "role": "user"
                }
            }), 201

        # 🔵 الحالة الثانية: بيانات FormData (Authority)
        else:
            print("📂 Processing Authority (FormData)...")
            role = request.form.get("role")
            
            if role != "authority":
                return jsonify({"message": "Invalid role"}), 400

            # (نفس كود الحفظ والملفات الخاص بالـ Authority)
            # تأكدي من إضافة mysql.connection.commit() هنا أيضاً في كودك
            # ...
            
            return jsonify({
                "message": "Authority created successfully",
                "role": "authority"
            }), 201

    except Exception as e:
        print(f"❌ DATABASE ERROR: {str(e)}")
        return jsonify({
            "message": "Internal Server Error",
            "error": str(e)
        }), 500