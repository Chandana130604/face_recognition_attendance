import face_recognition
import numpy as np
from models.employee_model import EmployeeModel

class FaceService:
    @staticmethod
    def get_face_encoding(image):
        """Return the 128‑dim encoding of the first face in the image."""
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb)
        if not encodings:
            return None
        return encodings[0]

    @staticmethod
    def recognize_face(encoding, threshold=0.6):
        """Compare with stored encodings and return best match."""
        all_emps = EmployeeModel.get_all_encodings()
        if not all_emps:
            return None
        stored_encodings = [np.array(emp['face_encoding']) for emp in all_emps]
        distances = face_recognition.face_distance(stored_encodings, encoding)
        min_dist = min(distances)
        if min_dist < threshold:
            idx = np.argmin(distances)
            return all_emps[idx]
        return None