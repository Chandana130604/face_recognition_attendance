import numpy as np
from models.employee_model import EmployeeModel

def get_face_encoding(face_image):
    """Simple flattened encoding – replace with deep model later."""
    resized = cv2.resize(face_image, (100, 100))
    return resized.flatten()

def recognize_face(face_encoding, threshold=5000):
    emp_model = EmployeeModel()
    all_encodings = emp_model.get_all_face_encodings()
    if not all_encodings:
        return None

    best_match = None
    min_diff = float('inf')
    for emp in all_encodings:
        stored = np.array(emp['face_encoding'])
        diff = np.linalg.norm(stored - face_encoding)
        if diff < threshold and diff < min_diff:
            min_diff = diff
            best_match = emp
    return best_match