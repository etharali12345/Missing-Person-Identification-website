import os 

class Config:

    SECRET_KEY = 'a9f823jkf93n2f0sdfn2398h23hfsd923hsdf923'
    # إعدادات الاتصال بقاعدة البيانات
    MYSQL_HOST = '127.0.0.1'       # أو IP السيرفر لو سيرفر خارجي
    MYSQL_USER = 'root'            # اسم المستخدم بتاعك
    MYSQL_PASSWORD = ''            # الباسورد بتاع MySQL
    MYSQL_DB = 'face_recognition_db'     # اسم قاعدة البيانات
    JWT_SECRET_KEY = "jwt-secret-string"
    UPLOAD_FOLDER = "uploads"