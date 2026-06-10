import os
from datetime import timedelta

class Config:
    SECRET_KEY          = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY      = os.environ.get('JWT_SECRET_KEY')
    MAIL_PASSWORD       = os.environ.get('MAIL_PASSWORD')

    MYSQL_HOST          = os.environ.get('MYSQLHOST')
    MYSQL_USER          = os.environ.get('MYSQLUSER')
    MYSQL_PASSWORD      = os.environ.get('MYSQLPASSWORD')
    MYSQL_DB            = os.environ.get('MYSQLDATABASE')

    MAIL_SERVER         = 'smtp.gmail.com'
    MAIL_PORT           = 587
    MAIL_USE_TLS        = True
    MAIL_USERNAME       = 'hopeplatform26@gmail.com'
    MAIL_DEFAULT_SENDER = 'hopeplatform26@gmail.com'

    UPLOAD_FOLDER           = 'static/uploads'
    JWT_TOKEN_LOCATION      = ['cookies']
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_ACCESS_COOKIE_NAME  = 'access_token_cookie'
    JWT_COOKIE_SAMESITE     = 'Lax'
    JWT_COOKIE_SECURE       = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)