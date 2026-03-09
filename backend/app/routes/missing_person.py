from flask import Blueprint, request, jsonify, current_app
from ..extensions import mysql
import os
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
FAISS_INDEX_PATH = "missing_persons.index"
DIMENSION = 512

def get_faiss_index():
    if os.path.exists(FAISS_INDEX_PATH):
        return faiss.read_index(FAISS_INDEX_PATH)
    else:
        return faiss.IndexFlatIP(DIMENSION)

# تحميل FAISS مرة واحدة
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
# API رفع بلاغ مفقود
# -----------------------------
@missing_person_bp.route("/report/send", methods=["POST"])
def send_report():

    try:

        data = request.form
        image = request.files.get("image_path")

        if not image:
            return jsonify({"message": "Image is required"}), 400

        # قراءة الصورة من request
        file_bytes = np.frombuffer(image.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"message": "Invalid image"}), 400

        # -----------------------------
        # اكتشاف الوجه
        # -----------------------------
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

            if len(faces) == 0:
                return jsonify({"message": "No faces found in the image"}), 400

        if len(faces) > 1:
            return jsonify({"error": "Multiple faces detected"}), 400

        # -----------------------------
        # استخراج الـ embedding
        # -----------------------------
        face = faces[0]

        embedding = face.normed_embedding.reshape(1, -1).astype('float32')

        faiss.normalize_L2(embedding)

        # -----------------------------
        # البحث في FAISS
        # -----------------------------
        threshold = 0.7

        if index.ntotal > 0:

            distances, indices = index.search(embedding, 1)

            similarity = float(distances[0][0])
            matched_id = int(indices[0][0])

            if similarity > threshold:

                return jsonify({
                    "message": "This person might already be reported!",
                    "matched_faiss_id": matched_id,
                    "similarity": similarity
                }), 200

        # -----------------------------
        # إضافة embedding جديد
        # -----------------------------
        new_faiss_id = index.ntotal

        index.add(embedding)

        faiss.write_index(index, FAISS_INDEX_PATH)

        # -----------------------------
        # حفظ الصورة
        # -----------------------------
        image.seek(0)

        filename = secure_filename(image.filename)

        filename = str(uuid.uuid4()) + "_" + filename

        upload_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"],
            filename
        )

        image.save(upload_path)

        # -----------------------------
        # حفظ البيانات في MySQL
        # -----------------------------
        cur = mysql.connection.cursor()

        cur.execute("""
        INSERT INTO missing_persons 
        (full_name, age, gender, last_seen_location, image_path, last_seen_date, phone_number1, phone_number2)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get("full_name"),
            data.get("age"),
            data.get("gender"),
            data.get("last_seen_location"),
            upload_path,
            data.get("last_seen_date"),
            data.get("phone_number1"),
            data.get("phone_number2")
        ))

        mysql.connection.commit()

        cur.close()

        return jsonify({
            "message": "Missing person report submitted successfully",
            "faiss_id": new_faiss_id
        }), 201

    except Exception as e:

        return jsonify({
            "message": "An error occurred",
            "error": str(e)
        }), 500