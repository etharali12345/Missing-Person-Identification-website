from flask import Flask
from flask_cors import CORS
from .config import Config
from .extensions import mysql, jwt
from .routes.auth import auth_bp
from .routes.missing_person import missing_person_bp
from .routes.found_person import found_person_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(
        app,
        supports_credentials=True,
        origins=["http://localhost:5173"],
        expose_headers=["set-cookie"]
    )

    mysql.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(missing_person_bp, url_prefix="/api")
    app.register_blueprint(found_person_bp, url_prefix="/api")

    return app