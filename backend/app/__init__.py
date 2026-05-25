from fileinput import filename
import os
from flask import Flask, app,send_from_directory, jsonify
from flask_cors import CORS
from .config import Config
from .extensions import mysql, jwt
from .routes.auth import auth_bp
from .routes.missing_person import missing_person_bp
from .routes.found_person import found_person_bp
from .routes.my_missing_cases import my_missing_bp
from .routes.my_found_cases import my_found_bp
from .extensions import mysql, jwt, mail
from .routes.admin import admin_bp #rawan should add

def create_app():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(root_dir, 'static')

    app = Flask(__name__, 
                static_folder=static_dir, 
                static_url_path='/static')
    app.config.from_object(Config)

    CORS(
        app,
        supports_credentials=True,
        origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174"
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
    
    @app.route('/static/uploads/<path:filename>')
    def serve_image(filename):
        print(f"[SERVE] filename requested: '{filename}'")
        print(f"[SERVE] static_dir: '{static_dir}'")
        uploads_dir = os.path.join(static_dir, 'uploads')
        full_path   = os.path.join(uploads_dir, filename)
        print(f"[SERVE] full_path: '{full_path}'")
        print(f"[SERVE] file exists: {os.path.exists(full_path)}")
        
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