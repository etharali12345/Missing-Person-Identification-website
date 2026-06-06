from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import mysql, mail
from flask_mail import Message
import threading

admin_bp = Blueprint("admin", __name__)

def send_email_async(app, msg):
    with app.app_context():
        mail.send(msg)

def admin_required():
    identity = get_jwt_identity()
    if not identity or identity.get("role") != "admin":
        return jsonify({"message": "Admin access required"}), 403
    return None


@admin_bp.route("/authorities", methods=["GET"])
@jwt_required()
def get_authorities():
    err = admin_required()
    if err:
        return err

    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            SELECT authority_id, authority_type, authority_name, status, created_at
            FROM authority
            ORDER BY created_at DESC
        """)
        rows = cur.fetchall()
        authorities = [
            {
                "authority_id": row[0],
                "authority_type": row[1],
                "authority_name": row[2],
                "status": row[3],
                "created_at": row[4].isoformat() if row[4] else None
            }
            for row in rows
        ]
        return jsonify(authorities), 200
    except Exception as e:
        return jsonify({"message": "فشل جلب البيانات", "error": str(e)}), 500
    finally:
        cur.close()


@admin_bp.route("/authorities/<int:authority_id>", methods=["GET"])
@jwt_required()
def get_authority_by_id(authority_id):
    err = admin_required()
    if err:
        return err

    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            SELECT authority_id, authority_type, authority_name,
                   email, location, document,
                   license_number, status, created_at
            FROM authority
            WHERE authority_id = %s
        """, (authority_id,))
        row = cur.fetchone()

        if not row:
            return jsonify({"message": "الجهة غير موجودة"}), 404

        authority = {
            "authority_id": row[0],
            "authority_type": row[1],
            "authority_name": row[2],
            "email": row[3],
            "location": row[4],
            "document": f"uploads/{row[5]}" if row[5] else None,
            "license_number": row[6],
            "status": row[7],
            "created_at": row[8].isoformat() if row[8] else None
        }
        return jsonify(authority), 200
    except Exception as e:
        return jsonify({"message": "فشل جلب البيانات", "error": str(e)}), 500
    finally:
        cur.close()


@admin_bp.route("/authorities/<int:authority_id>/status", methods=["PATCH"])
@jwt_required()
def update_authority_status(authority_id):
    err = admin_required()
    if err:
        return err

    data = request.get_json()
    status = data.get("status")

    if status not in ("pending", "approved", "rejected"):
        return jsonify({"message": "حالة غير صالحة"}), 400

    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT authority_name, email FROM authority WHERE authority_id = %s", (authority_id,))
        authority = cur.fetchone()

        if not authority:
            return jsonify({"message": "الجهة غير موجودة"}), 404

        authority_name = authority[0]
        email = authority[1]

        cur.execute("UPDATE authority SET status = %s WHERE authority_id = %s", (status, authority_id))
        mysql.connection.commit()

        messages = {
            "approved": "تهانينا! تم اعتماد حسابكم بنجاح. يمكنكم الان تسجيل الدخول.",
            "rejected": "نأسف لإبلاغكم بأنه تم رفض طلب تسجيل حسابكم.",
            "pending":  "تم إعادة حسابكم إلى قيد المراجعة."
        }

        msg = Message(
            subject="تحديث حالة حسابكم",
            recipients=[email],
        )

        msg.html = f"""
        <div dir="rtl" style="text-align:right;">
            <p>عزيزنا {authority_name}،</p>

            <p>{messages[status]}</p>

            <p>شكراً لكم.</p>
        </div>
        """

        msg.body = f"عزيزنا {authority_name}،\n\n{messages[status]}\n\nشكراً لكم."

        thread = threading.Thread(
            target=send_email_async,
            args=(current_app._get_current_object(), msg)
        )
        thread.start()

        return jsonify({"message": "تم تحديث الحالة وإرسال الإشعار"}), 200

    except Exception as e:
        return jsonify({"message": "فشل تحديث الحالة", "error": str(e)}), 500
    finally:
        cur.close()




@admin_bp.route("/dashboard-stats", methods=["GET"])
@jwt_required()
def dashboard_stats():
    err = admin_required()
    if err:
        return err

    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM authority WHERE status = 'pending'")
        pending_count = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) FROM missing_persons
            WHERE MONTH(created_at) = MONTH(CURDATE())
              AND YEAR(created_at) = YEAR(CURDATE())
        """)
        missing_this_month = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) FROM found_persons
            WHERE MONTH(created_at) = MONTH(CURDATE())
              AND YEAR(created_at) = YEAR(CURDATE())
        """)
        found_this_month = cur.fetchone()[0]

        return jsonify({
            "pending_count": pending_count,
            "missing_this_month": missing_this_month,
            "found_this_month": found_this_month,
        }), 200
    except Exception as e:
        return jsonify({"message": "فشل جلب البيانات", "error": str(e)}), 500
    finally:
        cur.close()