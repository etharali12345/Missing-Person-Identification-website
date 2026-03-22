from flask import Blueprint, request, jsonify, current_app
from ..extensions import mysql
import os
from MySQLdb.cursors import DictCursor
import cv2
import numpy as np
import uuid
from werkzeug.utils import secure_filename
from insightface.app import FaceAnalysis
import faiss

missing_person_bp = Blueprint("missing_person", __name__)

# -----------------------------
# إعدادات FAISS
# -----------------------------
FAISS_INDEX_PATH = "missing_datas.index"
DIMENSION = 512

def get_faiss_index():
    if os.path.exists(FAISS_INDEX_PATH):
        return faiss.read_index(FAISS_INDEX_PATH)
    else:
        return faiss.IndexFlatIP(DIMENSION)

# تحميل FAISS  
index = get_faiss_index()

# -----------------------------
# تحميل مودل التعرف على الوجه
# -----------------------------
device = -1  # CPU

face_model = FaceAnalysis(
    name='buffalo_l',
    providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
)

face_model.prepare(ctx_id=device, det_size=(640, 640))

# -----------------------------
#دالة قراءة  الصورة 
def read_image(image_file):
    try:
        file_bytes = np.frombuffer(image_file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        return img
    except:
        return None
# -----------------------------
#دالة اكتشاف الوجه
def detect_faces(img):        
    faces = face_model.get(img)
    if len(faces) == 0:
        h, w = img.shape[:2]
        pad_ratio = 0.3
        pad_h = int(h * pad_ratio)
        pad_w = int(w * pad_ratio)
        img = cv2.copyMakeBorder(
            img,
            pad_h,
            pad_h,
            pad_w,
            pad_w,
            cv2.BORDER_CONSTANT,
            value=(0, 0, 0)

        )
        faces = face_model.get(img)
    return faces, img
# -----------------------------
#دالة استخراج الemcedding
def get_embedding(face):

    embedding = face.normed_embedding.reshape(1, -1).astype('float32')
    faiss.normalize_L2(embedding)
    return embedding

# -----------------------------
#الدالة الخاصة ب مكتبةفايس

def search_faiss(embedding):
    if index.ntotal > 0:
        distances, indices = index.search(embedding, 1)
        similarity = float(distances[0][0])
        matched_id = int(indices[0][0])
        if matched_id == -1:
            return similarity, None
    return similarity, matched_id
# -----------------------------
#دالة حفظ الصورة

def save_image(image_file):

    image_file.seek(0)

    filename = secure_filename(image_file.filename)

    filename = f"{uuid.uuid4()}_{filename}"

    upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)

    image_file.save(upload_path)

    return upload_path, filename

#دالة حفظ البيانات في الداتا بيز

def save_to_db(data, upload_path, faiss_id, user_id):

    cur = mysql.connection.cursor(DictCursor)
    cur.execute("""
    INSERT INTO missing_persons
    (user_id,full_name, age, gender, last_seen_location, last_seen_date, phone_number1, phone_number2,image_path)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)
    """, (
        user_id,
        data.get("full_name"),
        data.get("age"),
        data.get("gender"),
        data.get("last_seen_location"),
        data.get("last_seen_date"),
        data.get("phone_number1"),
        data.get("phone_number2"),
        upload_path,
    ))
    mysql.connection.commit()
    person_id = cur.lastrowid
    cur.close()
    return person_id
#-----------------
def add_embedding_to_faiss(embedding, db_id):
    index.add_with_ids(
        embedding,
        np.array([db_id], dtype=np.int64)
    )
    faiss.write_index(index, FAISS_INDEX_PATH)
    return db_id
# -----------------------------

# -----------------------------

# -----------------------------

# -----------------------------
# API رفع بلاغ مفقود
# -----------------------------
@missing_person_bp.route("/report/send", methods=["POST"])
def send_report():

    try:

        data = request.form
        image = request.files.get("image_path")

        if not image:
            return jsonify({"message": "Image is required"}), 400
        img = read_image(image)
        if img is None:
            return jsonify({"message": "Invalid image file"}), 400
        faces, img = detect_faces(img)
        if len(faces) == 0:
                return jsonify({"message": "No faces found in the image"}), 400
        if len(faces) > 1:
            return jsonify({"error": "Multiple faces detected"}), 400
        embedding = get_embedding(faces[0])
        similarity, matched_id = search_faiss(embedding)
###==============================
#القيم اللي حتتم بيها  المقارنة
        THRESHOLD_MATCH = 0.677
        THRESHOLD_UNCERTAIN = 0.60
        if similarity >= THRESHOLD_MATCH and matched_id is not None:
            cur = mysql.connection.cursor(DictCursor)
            cur.execute(
                "SELECT * FROM found_persons WHERE faiss_id = %s",
                (matched_id,)
            )
            matched_person:dict = cur.fetchone()
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
                        "approximate_age": matched_person.get("approximate_age"),
                        "gender": matched_person.get("gender"),
                        "health_status": matched_person.get("health_status"),
                        "found_date": str(matched_person.get("found_date")), 
                        "found_location": matched_person.get("found_location"),
                        "image_path": f"/static/uploads/{web_image_name}",
                        "authority_name": matched_person.get("authority_name"),
                        "phone_number1": matched_person.get("phone_number1"),
                        "phone_number2": matched_person.get("phone_number2")
                    }
                }), 200

        # --- 2. حالة الشك ---
        elif THRESHOLD_UNCERTAIN <= similarity < THRESHOLD_MATCH and matched_id is not None:
            cur = mysql.connection.cursor(DictCursor)
            cur.execute("SELECT * FROM found_persons WHERE faiss_id = %s", (matched_id,))
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
                        "approximate_age": matched_person.get("approximate_age") or matched_person.get("age"),
                        "gender": matched_person.get("gender"),
                        "health_status": matched_person.get("health_status"),
                        "found_date": str(matched_person.get("found_date")),
                        "found_location": matched_person.get("found_location"),
                        "image_path": f"/static/uploads/{web_image_name}",
                        "authority_name": matched_person.get("authority_name"),
                        "phone_number1": matched_person.get("phone_number1"),
                        "phone_number2": matched_person.get("phone_number2")
                    }
                }), 200
        else:
            try:
                upload_path, filename = save_image(image)
                current_user_id = 6
                person_id =save_to_db(data, upload_path, None, current_user_id)
                add_embedding_to_faiss(embedding, person_id)
                return jsonify({
                    "status": "no_match",
                    "percentage": similarity,
                    "message": "تم حفظ البلاغ"
                }), 201
            except Exception as e:
                return jsonify({"message": f"خطأ حفظ: {str(e)}"}), 500
    except Exception as e:
        return jsonify({
            "message": "An error occurred",
            "error": str(e)
        }), 500