from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token
from ..extensions import mysql
import os

auth_bp = Blueprint("auth", __name__)