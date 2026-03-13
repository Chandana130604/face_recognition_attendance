import cv2
import numpy as np
import os
from pathlib import Path
import albumentations as A

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

augment = A.Compose([
    A.RandomBrightnessContrast(p=0.5),
    A.Rotate(limit=15, p=0.5),
    A.HorizontalFlip(p=0.3),
    A.GaussNoise(var_limit=(10.0, 50.0), p=0.2),
    A.Blur(blur_limit=3, p=0.2),
])

def process_employee(emp_name):
    input_dir = RAW_DATA_DIR / emp_name
    output_dir = PROCESSED_DIR / emp_name
    output_dir.mkdir(parents=True, exist_ok=True)

    for img_file in input_dir.glob("*.jpg"):
        img = cv2.imread(str(img_file))
        if img is None:
            continue
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(50,50))
        if len(faces) == 0:
            print(f"No face in {img_file}, skipping.")
            continue
        x, y, w, h = max(faces, key=lambda f: f[2]*f[3])
        face_crop = img[y:y+h, x:x+w]
        resized = cv2.resize(face_crop, (160, 160))

        out_path = output_dir / img_file.name
        cv2.imwrite(str(out_path), resized)

        for i in range(3):
            aug_img = augment(image=resized)['image']
            aug_path = output_dir / f"{img_file.stem}_aug{i}.jpg"
            cv2.imwrite(str(aug_path), aug_img)

    print(f"Processed {emp_name}.")

if __name__ == "__main__":
    employees = [d for d in RAW_DATA_DIR.iterdir() if d.is_dir()]
    for emp in employees:
        process_employee(emp.name)