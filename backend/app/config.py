import os 
from datetime import timedelta

class Config:
    FRONTEND_URL = os.environ.get("FRONTEND_URL")

    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-key')
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or os.environ.get('MYSQLHOST', '127.0.0.1')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or os.environ.get('MYSQLPORT', '3306'))
    MYSQL_USER = os.environ.get('MYSQL_USER') or os.environ.get('MYSQLUSER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    if MYSQL_PASSWORD is None:
        MYSQL_PASSWORD = os.environ.get('MYSQLPASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB') or os.environ.get('MYSQLDATABASE', 'face_recognition_db')
    
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-only-key')
    UPLOAD_FOLDER = "static/uploads"

    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_ACCESS_COOKIE_NAME = 'access_token_cookie' 
    JWT_COOKIE_SAMESITE = 'Lax'
    JWT_COOKIE_SECURE = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', '')

    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', '')