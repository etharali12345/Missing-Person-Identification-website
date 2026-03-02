import os 

class Config:

    SECRET_KEY = 'a9f823jkf93n2f0sdfn2398h23hfsd923hsdf923'
    # إعدادات الاتصال بقاعدة البيانات
    MYSQL_HOST = '127.0.0.1'       
    MYSQL_USER = 'root'            
    MYSQL_PASSWORD = ''            
    MYSQL_DB = 'face_recognition_db'     # اسم قاعدة البيانات
    JWT_SECRET_KEY = "jwt-secret-string"
    UPLOAD_FOLDER = "uploads"

    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_ACCESS_COOKIE_NAME = 'access_token_cookie' # اسم الكوكيز
    JWT_COOKIE_SAMESITE = 'Lax'
    JWT_COOKIE_SECURE = False