import numpy as np
import os
import sys
from pathlib import Path
import tensorflow as tf
import tensorflow_hub as hub
import cv2

sys.path.append(str(Path(__file__).parent.parent))
from src.config import DATA_PROCESSED_DIR, EMBEDDINGS_PATH, LABELS_PATH, TARGET_SIZE

# Load FaceNet model from TF Hub
model_url = "https://tfhub.dev/google/tf2-preview/mobilenet_v2/feature_vector/4"
# Alternatively, use a dedicated face recognition model like Facenet
# model_url = "https://tfhub.dev/google/facenet/1"  # 128-D embeddings

# For demonstration, we'll use a placeholder model; replace with actual face recognition model.
# In practice, use a pre-trained facenet model.
class DummyEmbedder:
    def __init__(self):
        self.input_shape = TARGET_SIZE + (3,)
    def predict(self, images):
        # Return random 128-D embeddings (replace with real model)
        return np.random.randn(len(images), 128)

embedder = DummyEmbedder()  # Replace with actual model

def load_images_and_labels():
    images = []
    labels = []
    employees = [d for d in os.listdir(DATA_PROCESSED_DIR) if os.path.isdir(os.path.join(DATA_PROCESSED_DIR, d))]
    label_map = {name: i for i, name in enumerate(employees)}

    for emp_name in employees:
        emp_dir = os.path.join(DATA_PROCESSED_DIR, emp_name)
        for img_file in os.listdir(emp_dir):
            img_path = os.path.join(emp_dir, img_file)
            img = cv2.imread(img_path)
            if img is None:
                continue
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            images.append(img_rgb)
            labels.append(label_map[emp_name])

    return np.array(images), np.array(labels), label_map

def generate_and_save_embeddings():
    images, labels, label_map = load_images_and_labels()
    # Preprocess: normalize to [0,1] and ensure correct shape
    images = images.astype(np.float32) / 255.0

    # Generate embeddings in batches
    embeddings = embedder.predict(images)

    # Save
    os.makedirs(os.path.dirname(EMBEDDINGS_PATH), exist_ok=True)
    np.save(EMBEDDINGS_PATH, embeddings)
    np.save(LABELS_PATH, labels)
    # Also save mapping
    with open(os.path.join(os.path.dirname(EMBEDDINGS_PATH), "label_map.txt"), "w") as f:
        for name, idx in label_map.items():
            f.write(f"{idx}:{name}\n")
    print(f"Saved embeddings for {len(images)} images.")

if __name__ == "__main__":
    generate_and_save_embeddings()