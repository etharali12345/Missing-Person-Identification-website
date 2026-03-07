from flask_wtf import FlaskForm
from flask_wtf.file import FileField,FileAllowed
from wtforms import StringField,PasswordField,SubmitField,BooleanField,TextAreaField
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token,jwt_required, get_jwt_identity, set_access_cookies,unset_jwt_cookies
from ..extensions import mysql
import os

missing_person = Blueprint("auth", __name__)
