from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Message
from ..extensions import mysql, mail

def send_pending_reminder(app):
    with app.app_context():
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT authority_id, authority_name, created_at
            FROM authority
            WHERE status = 'pending'
              AND created_at < NOW() - INTERVAL 1 MONTH
        """)
        rows = cur.fetchall()
        cur.close()

        if not rows:
            return

        lines = "\n".join(
            f"- ID: {r[0]} | {r[1]} | منذ: {r[2].strftime('%Y-%m-%d')}"
            for r in rows
        )

        msg = Message(
            subject="تذكير: طلبات معلقة تحتاج مراجعة",
            recipients=[app.config["ADMIN_EMAIL"]],
        )
        msg.body = f"الطلبات المعلقة منذ أكثر من شهر:\n\n{lines}"

        try:
            mail.send(msg)
        except Exception as e:
            print("Email error:", e)


def init_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=send_pending_reminder,
        args=[app],
        trigger="interval",
        weeks=4
    )
    scheduler.start()