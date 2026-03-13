import numpy as np
import os
from pathlib import Path
import cv2
from keras_facenet import FaceNet

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
EMBEDDINGS_DIR = BASE_DIR / "data" / "embeddings"
EMBEDDINGS_DIR.mkdir(exist_ok=True)

# Load FaceNet model
embedder = FaceNet()

def load_images_and_labels():
    images = []
    labels = []
    label_map = {}
    employees = [d for d in PROCESSED_DIR.iterdir() if d.is_dir()]
    for idx, emp_dir in enumerate(employees):
        label_map[idx] = emp_dir.name
        for img_file in emp_dir.glob("*.jpg"):
            img = cv2.imread(str(img_file))
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            images.append(img_rgb)
            labels.append(idx)
    return np.array(images), np.array(labels), label_map

def generate_and_save():
    images, labels, label_map = load_images_and_labels()
    print(f"Generating embeddings for {len(images)} images...")

    # FaceNet expects input of shape (None, 160, 160, 3) and values 0-255
    # The model already handles preprocessing
    embeddings = embedder.embeddings(images)

    # Save embeddings and labels
    np.save(EMBEDDINGS_DIR / "embeddings.npy", embeddings)
    np.save(EMBEDDINGS_DIR / "labels.npy", labels)

    # Save label map
    with open(EMBEDDINGS_DIR / "label_map.txt", "w") as f:
        for idx, name in label_map.items():
            f.write(f"{idx}:{name}\n")
    print("Embeddings saved.")

if __name__ == "__main__":
    generate_and_save()