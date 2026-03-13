import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python.vision import FaceDetector, FaceDetectorOptions, RunningMode
import numpy as np
from database import employees
from services.attendance_service import mark_attendance
from utils.face_encoding import get_face_encoding

# ----------------------------------------------------------------------
# Initialize MediaPipe FaceDetector (once)
# ----------------------------------------------------------------------
MODEL_PATH = 'blaze_face_short_range.tflite'

base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = FaceDetectorOptions(
    base_options=base_options,
    running_mode=RunningMode.IMAGE,
    min_detection_confidence=0.5
)
detector = FaceDetector.create_from_options(options)

def recognize_faces():
    # Load known employees from database
    known_encodings = []
    emp_ids = []

    for emp in employees.find():
        known_encodings.append(np.array(emp["encoding"]))
        emp_ids.append(emp["emp_id"])

    if not known_encodings:
        print("No employees registered yet.")
        return

    video = cv2.VideoCapture(0)

    while True:
        ret, frame = video.read()
        if not ret:
            break

        # Face detection
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = detector.detect(mp_image)

        if detection_result.detections:
            # Use the first detected face
            detection = detection_result.detections[0]
            bbox = detection.bounding_box

            # Crop the face
            h, w, _ = frame.shape
            x1 = max(0, bbox.origin_x)
            y1 = max(0, bbox.origin_y)
            x2 = min(w, bbox.origin_x + bbox.width)
            y2 = min(h, bbox.origin_y + bbox.height)

            if x2 > x1 and y2 > y1:
                face_crop = frame[y1:y2, x1:x2]
                encoding = get_face_encoding(face_crop)

                # Compare with known encodings
                for i, known in enumerate(known_encodings):
                    diff = np.linalg.norm(known - encoding)
                    if diff < 5000:   # threshold (adjust as needed)
                        emp_id = emp_ids[i]
                        print("Employee detected:", emp_id)
                        result = mark_attendance(emp_id)
                        print(result)
                        # Optional: break after first match
                        break

        cv2.imshow("Face Attendance", frame)
        if cv2.waitKey(1) == 27:
            break

    video.release()
    cv2.destroyAllWindows()