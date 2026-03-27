from ..services.face_service import FaceService
from .auth import get_current_user
from flask import Blueprint, request, jsonify, current_app
from ..extensions import mysql
import traceback
import os
from MySQLdb.cursors import DictCursor
import cv2
import numpy as np
import uuid
from werkzeug.utils import secure_filename
from insightface.app import FaceAnalysis
import faiss

found_person_bp = Blueprint("found_person", __name__)
face_service = None

def get_face_service():
    global face_service
    if face_service is None:
        path = os.path.join(current_app.instance_path, "persons_datas.index")
        face_service = FaceService(path)
    return face_service

#---------------------

device = -1  # CPU    
#دالة حفظ البيانات في الداتا بيز
def save_to_db(data, upload_path, faiss_id, user_id):

    cur = mysql.connection.cursor(DictCursor)
    cur.execute("""
    INSERT INTO found_persons
        (organization_id,full_name, approximate_age, gender,
        found_location, found_date,health_status,image_path,
        faiss_id,phone_number1, phone_number2)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s)
        """, ( 
        user_id,
        data.get("full_name"),
        data.get("approximate_age"),
        data.get("gender"),
        data.get("found_location"),
        data.get("found_date"),
        data.get("health_status"),
        upload_path,
        faiss_id,
        data.get("phone_number1"),
        data.get("phone_number2")
        
    ))
    mysql.connection.commit()
    person_id = cur.lastrowid
    cur.close()
    return person_id

# API رفع بلاغ مفقود
@found_person_bp.route("/found-report/send", methods=["POST"])
def send_report():

    try:
        face_service = get_face_service()
        data = request.form
        image = request.files.get("image_path") 
        index = face_service.get_faiss_index()

        if not image:
            return jsonify({"message": "Image is required"}), 400
        img = face_service.read_image(image)
        if img is None:
            return jsonify({"message": "Invalid image file"}), 400
        faces, img = face_service.detect_faces(img)
        if len(faces) == 0:
                return jsonify({"message": "No faces found in the image"}), 400
        if len(faces) > 1:
            return jsonify({"error": "Multiple faces detected"}), 400
        embedding = face_service.get_embedding(faces[0])
        similarity, matched_id = face_service.search(embedding)
 ###==============================
 #القيم اللي حتتم بيها  المقارنة
        THRESHOLD_MATCH = 0.677
        THRESHOLD_UNCERTAIN = 0.60
        if similarity >= THRESHOLD_MATCH and matched_id is not None:
            cur = mysql.connection.cursor(DictCursor)
            cur.execute("SELECT * FROM missing_persons WHERE faiss_id = %s",
                (matched_id,))
            matched_person = cur.fetchone()
            cur.close()
            if matched_person:
                db_path = matched_person.get("image_path")
                web_image_name = os.path.basename(db_path) if db_path else "default.jpg"
                return jsonify({
                    "status": "match",
                    "matchId": int(matched_id),
                    "percentage": similarity,
                    "details": {
                        "full_name": matched_person.get("full_name"),
                        "age": matched_person.get("approximate_age"),
                        "gender": matched_person.get("gender"),
                        "last_seen_date": str(matched_person.get("last_seen_date")),
                        "last_seen_location": matched_person.get("last_seen_location"),
                        "image_path": f"/static/uploads/{web_image_name}",
                        "phone_number1": matched_person.get("phone_number1"),
                        "phone_number2": matched_person.get("phone_number2")
                             }
                })  , 200
         # --- 2. حالة الشك ---
        elif THRESHOLD_UNCERTAIN <= similarity < THRESHOLD_MATCH and matched_id is not None:
            cur = mysql.connection.cursor(DictCursor)
            cur.execute("SELECT * FROM missing_persons WHERE faiss_id = %s", (matched_id,))
            matched_person = cur.fetchone()
            cur.close()
            if matched_person:
                db_path = matched_person.get("image_path")
                web_image_name = os.path.basename(db_path) if db_path else "default.jpg"

                return jsonify({
                    "status": "uncertain",
                    "matchId": int(matched_id),
                    "percentage": similarity,
                    "details": {
                        "full_name": matched_person.get("full_name"),
                        "age": matched_person.get("approximate_age"),
                        "gender": matched_person.get("gender"),
                        "last_seen_date": str(matched_person.get("last_seen_date")),
                        "last_seen_location": matched_person.get("last_seen_location"),
                        "image_path": f"/static/uploads/{web_image_name}",
                        "phone_number1": matched_person.get("phone_number1"),
                        "phone_number2": matched_person.get("phone_number2")
                             }
                })  , 200
        else:
            try:
                upload_path, filename = face_service.save_image(image)
                current_user_id = 5
                person_id =save_to_db(data, upload_path, None, current_user_id)
                faiss_id = person_id
                face_service.add_embedding_to_faiss(embedding, person_id)
                return jsonify({
                    "status": "no_match",
                    "matchId": None,
                    "percentage": similarity,
                    "details": None,
                    "message": "تم حفظ البلاغ"
                }), 201
            except Exception as e:
                return jsonify({"message": f"خطأ حفظ: {str(e)}"}), 500    
    except Exception as e:
        return jsonify({
            "message": "An error occurred",
            "error": str(e)
        }), 500