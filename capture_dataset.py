import cv2
import os

def capture_images(employee_name, num_images=20):
    save_dir = os.path.join('dataset', employee_name)
    os.makedirs(save_dir, exist_ok=True)

    cap = cv2.VideoCapture(0)
    count = 0
    print(f"Capturing {num_images} images for {employee_name}. Press SPACE to capture, 'q' to quit.")
    while count < num_images:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Capture", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            img_path = os.path.join(save_dir, f"img{count+1:02d}.jpg")
            cv2.imwrite(img_path, frame)
            print(f"Saved {img_path}")
            count += 1
        elif key == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    print(f"Captured {count} images.")

if __name__ == "__main__":
    name = input("Enter employee name: ").strip()
    if name:
        capture_images(name, 20)