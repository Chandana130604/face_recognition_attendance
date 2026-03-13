import cv2
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))
from src.config import DATA_RAW_DIR

def capture_faces(employee_name, num_images=50):
    """Capture images for a given employee."""
    save_dir = os.path.join(DATA_RAW_DIR, employee_name)
    os.makedirs(save_dir, exist_ok=True)

    cap = cv2.VideoCapture(0)
    count = 0

    print(f"Capturing faces for {employee_name}. Press SPACE to capture, 'q' to quit.")
    while count < num_images:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Capture", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):
            img_path = os.path.join(save_dir, f"{count:03d}.jpg")
            cv2.imwrite(img_path, frame)
            print(f"Saved {img_path}")
            count += 1
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"Captured {count} images for {employee_name}.")

if __name__ == "__main__":
    name = input("Enter employee name: ").strip()
    if name:
        capture_faces(name)