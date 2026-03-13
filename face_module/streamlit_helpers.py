import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python.vision import FaceDetector, FaceDetectorOptions, RunningMode
import numpy as np
from database import employees
from services.attendance_service import mark_attendance
from utils.face_encoding import get_face_encoding

# Initialize detector once (module level)
MODEL_PATH = 'blaze_face_short_range.tflite'
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = FaceDetectorOptions(
    base_options=base_options,
    running_mode=RunningMode.IMAGE,
    min_detection_confidence=0.5
)
detector = FaceDetector.create_from_options(options)

# Cache known encodings (will be reloaded on each call in Streamlit due to statelessness,
# but we can load once if we use st.cache_resource)
import streamlit as st

@st.cache_resource
def load_known_faces():
    """Load all registered employees into memory (cached)"""
    known_encodings = []
    emp_ids = []
    for emp in employees.find():
        known_encodings.append(np.array(emp["encoding"]))
        emp_ids.append(emp["emp_id"])
    return known_encodings, emp_ids

def register_face(frame, emp_id, name):
    """Register a new employee from a single frame"""
    try:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = detector.detect(mp_image)

        if not detection_result.detections:
            return {"success": False, "message": "No face detected"}

        detection = detection_result.detections[0]
        bbox = detection.bounding_box

        h, w, _ = frame.shape
        x1 = max(0, bbox.origin_x)
        y1 = max(0, bbox.origin_y)
        x2 = min(w, bbox.origin_x + bbox.width)
        y2 = min(h, bbox.origin_y + bbox.height)

        if x2 <= x1 or y2 <= y1:
            return {"success": False, "message": "Invalid face crop"}

        face_crop = frame[y1:y2, x1:x2]
        encoding = get_face_encoding(face_crop)

        # Check if employee already exists
        existing = employees.find_one({"emp_id": emp_id})
        if existing:
            return {"success": False, "message": "Employee ID already exists"}

        employees.insert_one({
            "emp_id": emp_id,
            "name": name,
            "encoding": encoding.tolist()
        })
        return {"success": True, "message": f"Employee {name} registered successfully"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

def recognize_face(frame):
    """Recognize a face from a single frame and mark attendance"""
    try:
        known_encodings, emp_ids = load_known_faces()
        if not known_encodings:
            return {"success": False, "message": "No employees registered"}

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = detector.detect(mp_image)

        if not detection_result.detections:
            return {"success": False, "message": "No face detected"}

        detection = detection_result.detections[0]
        bbox = detection.bounding_box

        h, w, _ = frame.shape
        x1 = max(0, bbox.origin_x)
        y1 = max(0, bbox.origin_y)
        x2 = min(w, bbox.origin_x + bbox.width)
        y2 = min(h, bbox.origin_y + bbox.height)

        if x2 <= x1 or y2 <= y1:
            return {"success": False, "message": "Invalid face crop"}

        face_crop = frame[y1:y2, x1:x2]
        encoding = get_face_encoding(face_crop)

        best_match = None
        min_diff = float('inf')
        for i, known in enumerate(known_encodings):
            diff = np.linalg.norm(known - encoding)
            if diff < 5000 and diff < min_diff:
                min_diff = diff
                best_match = emp_ids[i]

        if best_match:
            result = mark_attendance(best_match)
            return {
                "success": True,
                "emp_id": best_match,
                "message": result
            }
        else:
            return {"success": False, "message": "No matching employee found"}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}