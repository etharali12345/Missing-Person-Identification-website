from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash,check_password_hash
from flask_jwt_extended import create_access_token,jwt_required, get_jwt_identity, set_access_cookies,unset_jwt_cookies
from ..extensions import mysql
import os

auth_bp = Blueprint("auth", __name__)
