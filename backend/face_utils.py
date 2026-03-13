import cv2
import numpy as np
import logging
import face_recognition
from mtcnn import MTCNN
from config import Config

logger = logging.getLogger(__name__)

# Initialize models once (singleton pattern)
_detector = None
_haar_cascade = None

def get_detector():
    global _detector
    if _detector is None:
        _detector = MTCNN()
        logger.info("MTCNN detector initialised.")
    return _detector

def get_haar_cascade():
    global _haar_cascade
    if _haar_cascade is None:
        _haar_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        if _haar_cascade.empty():
            logger.error("Haar cascade XML not found.")
        else:
            logger.info("Haar cascade fallback initialised.")
    return _haar_cascade

def enhance_image_for_detection(img):
    """
    Apply histogram equalization on the L channel of LAB color space
    to improve contrast and help face detection in low‑light images.
    Returns enhanced RGB image.
    """
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    l_enhanced = clahe.apply(l)
    enhanced_lab = cv2.merge([l_enhanced, a, b])
    enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    return enhanced_bgr

class FaceUtils:
    @staticmethod
    def get_face_encoding(image_bytes):
        """
        Detect face using MTCNN (first) then fallback to Haar cascade,
        with optional image enhancement. Returns 128‑D embedding or None.
        """
        np_arr = np.frombuffer(image_bytes, np.uint8)
        if len(np_arr) == 0:
            logger.error("Empty image bytes.")
            return None
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            logger.error("cv2.imdecode failed.")
            return None

        enhanced = enhance_image_for_detection(img)
        rgb = cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB)
        h, w, _ = enhanced.shape
        logger.debug(f"Image shape: {w}x{h}")

        detector = get_detector()
        results = detector.detect_faces(rgb)
        logger.debug(f"MTCNN found {len(results)} faces")
        face_location = None

        if len(results) > 0:
            face = max(results, key=lambda x: x['box'][2] * x['box'][3])
            x, y, box_w, box_h = face['box']
            x, y = max(0, x), max(0, y)
            box_w = min(box_w, w - x)
            box_h = min(box_h, h - y)
            if box_w > 0 and box_h > 0:
                top, right, bottom, left = y, x+box_w, y+box_h, x
                face_location = (top, right, bottom, left)
                logger.debug(f"MTCNN: face at ({top},{left}) size {box_w}x{box_h}")
            else:
                logger.warning("MTCNN returned invalid box dimensions.")
        else:
            logger.debug("MTCNN found no face; trying Haar cascade.")
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            haar = get_haar_cascade()
            if haar is not None and not haar.empty():
                faces_haar = haar.detectMultiScale(gray, 1.1, 4, minSize=(50,50))
                logger.debug(f"Haar cascade found {len(faces_haar)} faces")
                if len(faces_haar) > 0:
                    x, y, box_w, box_h = max(faces_haar, key=lambda f: f[2]*f[3])
                    top, right, bottom, left = y, x+box_w, y+box_h, x
                    face_location = (top, right, bottom, left)
                    logger.debug(f"Haar: face at ({top},{left}) size {box_w}x{box_h}")
                else:
                    logger.warning("No face detected by any detector.")
                    return None
            else:
                logger.error("Haar cascade not available.")
                return None

        if face_location is None:
            logger.warning("Face location is None.")
            return None

        try:
            original_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(original_rgb, [face_location])
            if len(encodings) == 0:
                logger.warning("face_recognition returned no encodings.")
                return None
            embedding = encodings[0]
        except Exception as e:
            logger.error(f"face_recognition failed: {e}")
            return None

        logger.debug(f"Embedding generated, shape {embedding.shape}")
        return embedding.tolist()

    @staticmethod
    def compare_faces(known_encodings, face_encoding, tolerance=Config.FACE_MATCH_TOLERANCE):
        """
        Compare face encoding against a list of known encodings.
        Returns (best_index, distance) if match found, else (None, None).
        Uses Euclidean distance (face_recognition's default).
        """
        if not known_encodings:
            logger.warning("No known encodings to compare.")
            return None, None

        known = np.array(known_encodings)
        face = np.array(face_encoding)

        distances = np.linalg.norm(known - face, axis=1)
        best_idx = np.argmin(distances)
        best_dist = distances[best_idx]
        logger.debug(f"Best match distance: {best_dist:.4f}")

        if best_dist <= tolerance:
            return best_idx, best_dist
        logger.debug(f"Best distance {best_dist} exceeds tolerance {tolerance}")
        return None, None