import numpy as np
import cv2
import joblib
from pathlib import Path
from keras_facenet import FaceNet
from mtcnn import MTCNN

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"

# Load trained classifier and label map
clf = joblib.load(MODEL_DIR / "classifier.pkl")
label_map = {}
with open(MODEL_DIR / "label_map.txt", "r") as f:
    for line in f:
        idx, name = line.strip().split(":")
        label_map[int(idx)] = name

# Load FaceNet embedder
embedder = FaceNet()

# Initialize detector
detector = MTCNN()

def recognize_face(face_img):
    """
    face_img: BGR image (numpy array) cropped to face.
    Returns (employee_name, confidence) or (None, None).
    """
    # Preprocess: convert to RGB, resize to 160x160
    rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
    resized = cv2.resize(rgb, (160, 160))
    # Expand dims to (1,160,160,3)
    img_array = np.expand_dims(resized, axis=0)

    # Generate embedding
    embedding = embedder.embeddings(img_array)[0]  # shape (128,)

    # Predict probability
    probs = clf.predict_proba([embedding])[0]
    best_idx = np.argmax(probs)
    confidence = probs[best_idx]

    if confidence > 0.7:  # threshold
        return label_map[best_idx], confidence
    else:
        return None, None