import cv2
import numpy as np
import os
import sys
from pathlib import Path
from mtcnn import MTCNN
import albumentations as A

sys.path.append(str(Path(__file__).parent.parent))
from src.config import DATA_RAW_DIR, DATA_PROCESSED_DIR, TARGET_SIZE

detector = MTCNN()

# Augmentation pipeline
augment = A.Compose([
    A.RandomBrightnessContrast(p=0.5),
    A.Rotate(limit=15, p=0.5),
    A.HorizontalFlip(p=0.3),
    A.GaussNoise(var_limit=(10.0, 50.0), p=0.2),
    A.Blur(blur_limit=3, p=0.2),
])

def align_face(image, keypoints):
    """Simple alignment based on eyes (if available)."""
    left_eye = keypoints['left_eye']
    right_eye = keypoints['right_eye']
    # Compute angle between eyes
    dy = right_eye[1] - left_eye[1]
    dx = right_eye[0] - left_eye[0]
    angle = np.degrees(np.arctan2(dy, dx))
    # Rotate around the center
    center = tuple(np.array(image.shape[:2]) / 2)
    rot_mat = cv2.getRotationMatrix2D(center, angle, 1.0)
    aligned = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return aligned

def process_employee(emp_name):
    input_dir = os.path.join(DATA_RAW_DIR, emp_name)
    output_dir = os.path.join(DATA_PROCESSED_DIR, emp_name)
    os.makedirs(output_dir, exist_ok=True)

    for img_file in os.listdir(input_dir):
        img_path = os.path.join(input_dir, img_file)
        img = cv2.imread(img_path)
        if img is None:
            continue
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Detect faces
        results = detector.detect_faces(rgb)
        if len(results) == 0:
            print(f"No face in {img_file}, skipping.")
            continue
        # Take the largest face
        face = max(results, key=lambda x: x['box'][2]*x['box'][3])
        x, y, w, h = face['box']
        x, y = max(0, x), max(0, y)
        face_crop = rgb[y:y+h, x:x+w]

        # Align if desired
        if 'keypoints' in face:
            aligned = align_face(face_crop, face['keypoints'])
        else:
            aligned = face_crop

        # Resize to target size
        resized = cv2.resize(aligned, TARGET_SIZE)

        # Save the processed face
        out_path = os.path.join(output_dir, img_file)
        cv2.imwrite(out_path, cv2.cvtColor(resized, cv2.COLOR_RGB2BGR))

        # Generate augmented versions (optional)
        for i in range(3):  # create 3 augmented copies
            aug_img = augment(image=resized)['image']
            aug_path = os.path.join(output_dir, f"{os.path.splitext(img_file)[0]}_aug{i}.jpg")
            cv2.imwrite(aug_path, cv2.cvtColor(aug_img, cv2.COLOR_RGB2BGR))

    print(f"Processed {emp_name}.")

if __name__ == "__main__":
    employees = [d for d in os.listdir(DATA_RAW_DIR) if os.path.isdir(os.path.join(DATA_RAW_DIR, d))]
    for emp in employees:
        process_employee(emp)