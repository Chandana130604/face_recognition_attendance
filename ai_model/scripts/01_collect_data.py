import cv2
import os
import sys
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = BASE_DIR / "data" / "raw"

def collect_data(employee_name, num_samples=50):
    """Capture num_samples images for the given employee."""
    save_dir = RAW_DATA_DIR / employee_name
    save_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(0)
    count = 0

    print(f"Collecting data for {employee_name}. Press SPACE to capture, 'q' to quit.")
    while count < num_samples:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Capture", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):
            img_path = save_dir / f"{count:03d}.jpg"
            cv2.imwrite(str(img_path), frame)
            print(f"Saved {img_path}")
            count += 1
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Collected {count} images for {employee_name}.")

if __name__ == "__main__":
    name = input("Enter employee name: ").strip()
    if name:
        collect_data(name)