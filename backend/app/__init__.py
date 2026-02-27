from flask import Flask
from flask_cors import CORS
from .config import Config
from .extensions import mysql, jwt
from .routes.auth import auth_bp

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    app.config.from_object(Config)

    # initialize extensions
    mysql.init_app(app)
    jwt.init_app(app)

    # register blueprints
    app.register_blueprint(auth_bp, url_prefix="/api//auth")

    return app