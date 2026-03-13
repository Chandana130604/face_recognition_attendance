import face_recognition
import numpy as np
import logging
import tempfile
import os
from backend.employee_manager import EmployeeManager

logger = logging.getLogger(__name__)

class FaceEngine:
    @staticmethod
    def get_encoding_from_image(image_bytes):
        """Used for registration: returns encoding or None."""
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f:
                f.write(image_bytes)
                temp_file = f.name

            image = face_recognition.load_image_file(temp_file)
            face_locations = face_recognition.face_locations(image, model='hog')
            if not face_locations:
                face_locations = face_recognition.face_locations(image, model='cnn')
            if not face_locations:
                return None
            encodings = face_recognition.face_encodings(image, face_locations)
            if encodings:
                return encodings[0].tolist()
            return None
        except Exception as e:
            logger.error(f"Error in get_encoding_from_image: {e}")
            return None
        finally:
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)

    @staticmethod
    def recognize_face(image_bytes, emp_mgr=None):
        if emp_mgr is None:
            emp_mgr = EmployeeManager()

        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as f:
                f.write(image_bytes)
                temp_file = f.name

            image = face_recognition.load_image_file(temp_file)
            face_locations = face_recognition.face_locations(image, model='hog')
            if not face_locations:
                face_locations = face_recognition.face_locations(image, model='cnn')
            if not face_locations:
                return None, None

            face_encodings = face_recognition.face_encodings(image, face_locations)
            if not face_encodings:
                return None, None
            face_encoding = face_encodings[0]

            employees = emp_mgr.get_all_employees()
        # Flatten all encodings with references to employee
            all_encodings = []
            emp_ids = []
            names = []
            for emp in employees:
                enc_list = emp.get('face_encoding', [])
                for enc in enc_list:
                    all_encodings.append(enc)
                    emp_ids.append(emp['emp_id'])
                    names.append(emp['name'])

            if not all_encodings:
                return None, None

            known_np = np.array(all_encodings)
            face_np = np.array(face_encoding)
            distances = np.linalg.norm(known_np - face_np, axis=1)
            best_idx = np.argmin(distances)
            best_distance = distances[best_idx]

            TOLERANCE = 0.5
            if best_distance <= TOLERANCE:
                return emp_ids[best_idx], names[best_idx]
            return None, None

        except Exception as e:
            logger.error(f"Error in recognize_face: {e}", exc_info=True)
            return None, None
        finally:
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)