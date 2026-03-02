from flask import Flask
from flask_cors import CORS
from .config import Config
from .extensions import mysql, jwt
from .routes.auth import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:5173", "http://127.0.0.1:5173"]
        )
    mysql.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/api//auth")

    return app