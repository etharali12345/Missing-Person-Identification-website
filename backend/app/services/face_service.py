from flask import current_app, jsonify
from werkzeug.utils import secure_filename
import os
import cv2
import numpy as np
import faiss
from insightface.app import FaceAnalysis
import uuid

#تجهيز المودل الخاص بالتعرف على الوجه
class FaceService:
    DIMENSION = 512

    def __init__(self, faiss_path):
        self.FAISS_INDEX_PATH = faiss_path

        self.index = self.get_faiss_index()

        self.face_model = FaceAnalysis(
            name='buffalo_l',
            providers=['CPUExecutionProvider']
        )
        self.face_model.prepare(ctx_id=-1, det_size=(640, 640))

# -----------------------------
# تحميل مودل التعرف على الوجه
# -----------------------------
    def get_faiss_index(self):
        if os.path.exists(self.FAISS_INDEX_PATH):
            return faiss.read_index(self.FAISS_INDEX_PATH)

        base_index = faiss.IndexFlatIP(self.DIMENSION)
        return faiss.IndexIDMap(base_index)

# -----------------------------
#دالة قراءة  الصورة من الملف
    def read_image(self, image_file):
        try:
            file_bytes = np.frombuffer(image_file.read(), np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            return img
        except Exception as e:
            return jsonify({"error": "Error reading image: " + str(e)}), 400

    # -----------------
    #دالة اكتشاف الوجه

    def detect_faces(self, img):
        faces = self.face_model.get(img)
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
            faces = self.face_model.get(img)
        return faces, img

    # -----------------
    #دالة استخراج الemcedding
    def get_embedding(self, face):
        embedding = face.normed_embedding.reshape(1, -1).astype('float32')
        faiss.normalize_L2(embedding)
        return embedding

    # -----------------
    #الدالة الخاصة ب مكتبةفايس
    def search(self, embedding):
        if self.index.ntotal > 0:
            distances, indices = self.index.search(embedding, 1)
            similarity = float(distances[0][0])
            matched_id = int(indices[0][0])
            if matched_id == -1:
                return similarity, None
            return similarity, matched_id
        return 0.0, None
    #دالة حفظ الصورة

    def save_image(self, image_file):

        image_file.seek(0)
        filename = secure_filename(image_file.filename)
        filename = f"{uuid.uuid4()}_{filename}"
        upload_folder = current_app.config["UPLOAD_FOLDER"]
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)
        upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        image_file.save(upload_path)

        return upload_path, filename
    #-----------------
    def add_embedding_to_faiss(self,embedding, db_id):
        self.index.add_with_ids(
            embedding,
            np.array([db_id], dtype=np.int64)
        )
        faiss.write_index(self.index, self.FAISS_INDEX_PATH)
        return db_id