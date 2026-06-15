from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash,check_password_hash
from flask_jwt_extended import create_access_token,jwt_required, get_jwt_identity, set_access_cookies,unset_jwt_cookies
from ..extensions import mysql
import os
from MySQLdb import IntegrityError
import uuid
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup():
    try:
        if request.is_json:
            data = request.get_json()
            role = data.get("role")

            if role != "user":
                return jsonify({"message": "Invalid role for this endpoint"}), 400

            required = ["first_name", "last_name", "email_or_phone", "password"]
            missing = [f for f in required if not data.get(f)]
            if missing:
                return jsonify({"message": f"الحقول التالية مطلوبة: {', '.join(missing)}"}), 400

            hashed_password = generate_password_hash(data["password"])

            cur = mysql.connection.cursor()
            try:
                cur.execute("""
                    INSERT INTO users (first_name, last_name, email_or_phone, password, role)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    data["first_name"],
                    data["last_name"],
                    data["email_or_phone"],
                    hashed_password,
                    "user"
                ))
                mysql.connection.commit()
                user_id = cur.lastrowid
            except IntegrityError:
                return jsonify({"message": "البريد الإلكتروني أو رقم الهاتف مسجل مسبقاً"}), 409
            finally:
                cur.close()

            access_token = create_access_token(identity={
                "id": user_id,
                "role": "user"
            })

            response = jsonify({
                "message": "User created successfully",
                "user": {
                    "role": "user"
                }
            })
            set_access_cookies(response, access_token)
            return response, 201

        else:
            role = request.form.get("role")
            if role != "authority":
                return jsonify({"message": "Invalid role"}), 400
            

            required = ["authority_type", "authority_name", "email", "password", "location",]
            missing = [f for f in required if not request.form.get(f)]
            if missing:
                return jsonify({"message": f"الحقول التالية مطلوبة: {', '.join(missing)}"}), 400

            document = request.files.get("document")
            doc_path = None

            if not document or not allowed_file(document.filename):
                return jsonify({"message": "المستند المرفوع غير صالح أو مفقود"}), 400

            ext = document.filename.rsplit('.', 1)[1].lower()
            unique_name = f"{uuid.uuid4().hex}.{ext}"
            doc_path = f"authority_docs/{unique_name}"

            auth_type = request.form.get("authority_type")
            auth_name = request.form.get("authority_name")
            email = request.form.get("email")
            password = generate_password_hash(request.form.get("password"))
            location = request.form.get("location")
            license_num = request.form.get("license_number")

            cur = mysql.connection.cursor()
            try:
                cur.execute("""
                    INSERT INTO authority
                        (authority_type, authority_name, email, password,
                         location, license_number, status, document)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (auth_type, auth_name, email, password,
                      location, license_num, "pending", doc_path))
                mysql.connection.commit()

                root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                save_dir = os.path.join(root_dir, 'static', 'uploads', 'authority_docs')
                os.makedirs(save_dir, exist_ok=True)
                full_save_path = os.path.join(save_dir, unique_name)
                document.save(full_save_path)

            except IntegrityError:
                return jsonify({"message": "البريد الإلكتروني مسجل مسبقاً"}), 409
            finally:
                cur.close()

            response = jsonify({
                "message": "Authority request submitted successfully (Pending Approval)",
            })

            return response, 201
    except Exception as e:
        return jsonify({"message": "فشل انشاء الحساب", "error": str(e)}), 500
    


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email_or_phone = data.get("email_or_phone")
        password = data.get("password")
        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM users WHERE email_or_phone = %s", (email_or_phone,))
        user = cur.fetchone()

        if user and check_password_hash(user[5], password): 
            cur.close()
            user_id = user[0]
            role    = user[1]

            access_token = create_access_token(identity={
                "id":    user_id,
                "role":  role
            })

            response = jsonify({
                "message": "Login successful",
                "user": {"role": role} 
            })

            set_access_cookies(response, access_token)
            return response, 200

        cur.execute("SELECT * FROM authority WHERE email = %s", (email_or_phone,))
        auth_user = cur.fetchone()
        cur.close()

        if auth_user and check_password_hash(auth_user[4], password):  
            status = auth_user[8] 

            if status == "pending":
                return jsonify({
                    "message": "طلبك لا يزال قيد المراجعة. يرجى الانتظار حتى يتم اعتماده"
                }), 403

            if status == "rejected":
                return jsonify({
                    "message": "تم رفض طلب تسجيل حسابك."
                }), 403

            access_token = create_access_token(identity={
                "id":    auth_user[0],
                "role":  "authority"
            })

            response = jsonify({
                "message": "Login successful",
                "user": {"role": "authority"}
            })
            set_access_cookies(response, access_token)
            return response, 200

        return jsonify({"message": "بيانات الدخول غير صحيحة"}), 401

    except Exception as e:
        return jsonify({"message": "Internal Server Error", "error": str(e)}), 500


@auth_bp.route("/me", methods=["GET"])
@jwt_required() 
def get_current_user():
    try:
        current_identity = get_jwt_identity()
        role = current_identity.get("role")
        user_id = current_identity.get("id")

        if not role:
            return jsonify({"message": "Invalid token"}), 401

        return jsonify({
            "user": {
                "id":   user_id,
                "role": role
            }
        }), 200

    except Exception as e:
        return jsonify({"message": "Server error", "error": str(e)}), 500
    


@auth_bp.route("/logout", methods=["POST"])
def logout():
    resp = jsonify({"message": "Successfully logged out"})
    unset_jwt_cookies(resp)
    return resp, 200

