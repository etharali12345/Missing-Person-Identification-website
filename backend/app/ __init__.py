from flask import Flask
from .config import Config
from .extensions import mysql, jwt
from .routes.auth import auth_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # initialize extensions
    mysql.init_app(app)
    jwt.init_app(app)

    # register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app