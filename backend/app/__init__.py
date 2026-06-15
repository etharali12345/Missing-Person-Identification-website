from fileinput import filename
import os
from flask import Flask, app,send_from_directory, jsonify
from flask_cors import CORS
from .extensions import mysql, jwt
from .routes.auth import auth_bp
from .routes.missing_person import missing_person_bp
from .routes.found_person import found_person_bp
from .routes.my_missing_cases import my_missing_bp
from .routes.my_found_cases import my_found_bp
from .extensions import mysql, jwt, mail
from .routes.admin import admin_bp 
from .routes.missing_database import missing_db_bp
from .routes.found_database import found_db_bp
from .routes.user_profile import user_profile_bp
from .routes.scheduler import init_scheduler
from .services.face_service import preload_models

def create_app():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(root_dir, 'static')

    app = Flask(__name__, 
                static_folder=static_dir, 
                static_url_path='/static')
    
    try:
        from .config import Config
        app.config.from_object(Config)  
    except:
        app.config.from_object('config_railway.Config')  

    CORS(
        app,
        supports_credentials=True,
        origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "https://missing-person-identification-websi.vercel.app"
    ],
        expose_headers=["set-cookie"]
    )

    mysql.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(missing_person_bp, url_prefix="/api")
    app.register_blueprint(found_person_bp, url_prefix="/api")
    app.register_blueprint(my_missing_bp, url_prefix="/api")
    app.register_blueprint(my_found_bp, url_prefix="/api")
    app.register_blueprint(missing_db_bp, url_prefix="/api")
    app.register_blueprint(found_db_bp, url_prefix="/api")
    app.register_blueprint(user_profile_bp, url_prefix="/api")
    init_scheduler(app)

    preload_models()

    @app.route('/static/uploads/<path:filename>')
    def serve_image(filename):
        uploads_dir = os.path.join(static_dir, 'uploads')
        full_path   = os.path.join(uploads_dir, filename)
        return send_from_directory(uploads_dir, filename)
    

    @app.route('/uploads/<path:filename>')
    def serve_file(filename):
            uploads_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
            return send_from_directory(uploads_dir, filename)


    @app.route('/')
    def health_check():
        try:
            conn = mysql.connection
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            return jsonify({
                'status': 'running',
                'database': 'connected'
            })
        except Exception as e:
            return jsonify({
                'status': 'running',
                'database': f'not connected {str(e)}'
            })
        
    
    return app