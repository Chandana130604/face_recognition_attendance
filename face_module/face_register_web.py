import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python.vision import FaceDetector, FaceDetectorOptions, RunningMode
from database import employees
from utils.face_encoding import get_face_encoding
import numpy as np

# Initialize detector (same as before)
MODEL_PATH = 'blaze_face_short_range.tflite'
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = FaceDetectorOptions(
    base_options=base_options,
    running_mode=RunningMode.IMAGE,
    min_detection_confidence=0.5
)
detector = FaceDetector.create_from_options(options)

def register_employee_web(frame, emp_id, name):
    """Process a single frame for registration and return result"""
    try:
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = detector.detect(mp_image)
        
        if not detection_result.detections:
            return {"success": False, "message": "No face detected"}
        
        # Use first detected face
        detection = detection_result.detections[0]
        bbox = detection.bounding_box
        
        # Crop face
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
        
        # Insert into database
        employees.insert_one({
            "emp_id": emp_id,
            "name": name,
            "encoding": encoding.tolist()
        })
        
        return {"success": True, "message": f"Employee {name} registered successfully"}
        
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}