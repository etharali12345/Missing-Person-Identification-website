from insightface.app import FaceAnalysis
import cv2

app = FaceAnalysis(providers=['CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640))

img = cv2.imread("test.jpg")  # صورة في نفس الفولدر
faces = app.get(img)

print(f"Found {len(faces)} face(s)")