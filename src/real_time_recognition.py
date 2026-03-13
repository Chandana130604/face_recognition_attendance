import cv2
import numpy as np
import sys
from pathlib import Path
import time
from mtcnn import MTCNN

sys.path.append(str(Path(__file__).parent.parent))
from src.config import EMBEDDINGS_PATH, LABELS_PATH, SIMILARITY_THRESHOLD, CAMERA_ID, FRAME_SKIP
# Use the same embedder as above (or a separate instance)
from src.generate_embeddings import embedder

# Load stored embeddings and labels
embeddings = np.load(EMBEDDINGS_PATH)
labels = np.load(LABELS_PATH)
# Load label mapping
label_map = {}
with open(Path(EMBEDDINGS_PATH).parent / "label_map.txt", "r") as f:
    for line in f:
        idx, name = line.strip().split(":")
        label_map[int(idx)] = name

detector = MTCNN()

def recognize_face(face_img):
    """Return (name, distance) for a given face image."""
    face_resized = cv2.resize(face_img, (160, 160))
    face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)
    face_norm = face_rgb.astype(np.float32) / 255.0
    face_norm = np.expand_dims(face_norm, axis=0)

    embedding = embedder.predict(face_norm)[0]

    # Compute cosine distances
    distances = np.linalg.norm(embeddings - embedding, axis=1)
    best_idx = np.argmin(distances)
    best_dist = distances[best_idx]

    if best_dist < SIMILARITY_THRESHOLD:
        name = label_map[labels[best_idx]]
        return name, best_dist
    return None, best_dist

def main():
    cap = cv2.VideoCapture(CAMERA_ID)
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % FRAME_SKIP != 0:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = detector.detect_faces(rgb)

        for face in faces:
            x, y, w, h = face['box']
            x, y = max(0, x), max(0, y)
            face_crop = frame[y:y+h, x:x+w]
            name, dist = recognize_face(face_crop)

            # Draw box and label
            color = (0, 255, 0) if name else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            if name:
                label = f"{name} ({dist:.2f})"
            else:
                label = "Unknown"
            cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        cv2.imshow("Face Recognition", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()