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
    Apply CLAHE on the L channel of LAB color space to improve contrast
    and help face detection in low-light images. Returns enhanced BGR image.
    """
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l)
    enhanced_lab = cv2.merge([l_enhanced, a, b])
    enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
    return enhanced_bgr

def to_valid_rgb(img_bgr):
    """
    Convert a BGR image to a contiguous uint8 RGB image suitable for
    face_recognition / dlib. Handles gray, BGRA, and non-contiguous arrays.
    """
    # Handle grayscale
    if len(img_bgr.shape) == 2:
        img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_GRAY2BGR)
    # Handle BGRA (4 channels)
    elif img_bgr.shape[2] == 4:
        img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_BGRA2BGR)

    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

    # Ensure uint8
    if rgb.dtype != np.uint8:
        rgb = rgb.astype(np.uint8)

    # CRITICAL: dlib requires C-contiguous memory layout
    rgb = np.ascontiguousarray(rgb, dtype=np.uint8)
    return rgb


class FaceUtils:
    @staticmethod
    def get_face_encoding(image_bytes):
        """
        Detect face using MTCNN (first) then fallback to Haar cascade,
        with optional image enhancement. Returns 128-D embedding or None.
        """
        # Convert bytes to image
        np_arr = np.frombuffer(image_bytes, np.uint8)
        if len(np_arr) == 0:
            logger.error("Empty image bytes.")
            return None

        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            logger.error("cv2.imdecode failed.")
            return None

        # Enhance image for better detection
        enhanced = enhance_image_for_detection(img)
        rgb_enhanced = to_valid_rgb(enhanced)
        h, w = rgb_enhanced.shape[:2]
        logger.debug(f"Image shape: {w}x{h}")

        # ---- MTCNN detection ----
        detector = get_detector()
        results = detector.detect_faces(rgb_enhanced)
        logger.debug(f"MTCNN found {len(results)} faces")
        face_location = None

        if len(results) > 0:
            # Take the largest face
            face = max(results, key=lambda x: x['box'][2] * x['box'][3])
            x, y, box_w, box_h = face['box']
            x, y = max(0, x), max(0, y)
            box_w = min(box_w, w - x)
            box_h = min(box_h, h - y)
            if box_w > 0 and box_h > 0:
                # face_recognition expects (top, right, bottom, left)
                top, right, bottom, left = y, x + box_w, y + box_h, x
                face_location = (top, right, bottom, left)
                logger.debug(f"MTCNN: face at ({top},{left}) size {box_w}x{box_h}")
            else:
                logger.warning("MTCNN returned invalid box dimensions.")
        else:
            # ---- Fallback: Haar cascade ----
            logger.debug("MTCNN found no face; trying Haar cascade.")
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            haar = get_haar_cascade()
            if haar is not None and not haar.empty():
                faces_haar = haar.detectMultiScale(gray, 1.1, 4, minSize=(50, 50))
                logger.debug(f"Haar cascade found {len(faces_haar)} faces")
                if len(faces_haar) > 0:
                    x, y, box_w, box_h = max(faces_haar, key=lambda f: f[2] * f[3])
                    top, right, bottom, left = y, x + box_w, y + box_h, x
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

        # Generate encoding using original (non-enhanced) image for better accuracy
        try:
            original_rgb = to_valid_rgb(img)
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
        Handles inhomogeneous/corrupted encodings gracefully.
        """
        if not known_encodings:
            logger.warning("No known encodings to compare.")
            return None, None

        # Filter and flatten encodings — handles corrupted/nested data from MongoDB
        clean_encodings = []
        clean_indices = []
        for i, enc in enumerate(known_encodings):
            try:
                arr = np.array(enc, dtype=np.float64).flatten()
                if arr.shape == (128,):
                    clean_encodings.append(arr)
                    clean_indices.append(i)
                else:
                    logger.warning(f"Skipping encoding at index {i}: shape {arr.shape}")
            except Exception as e:
                logger.warning(f"Skipping invalid encoding at index {i}: {e}")

        if not clean_encodings:
            logger.warning("No valid encodings after filtering.")
            return None, None

        known = np.array(clean_encodings)
        face = np.array(face_encoding, dtype=np.float64).flatten()

        if face.shape != (128,):
            logger.error(f"Invalid face encoding shape: {face.shape}")
            return None, None

        # Compute Euclidean distances
        distances = np.linalg.norm(known - face, axis=1)
        best_local_idx = np.argmin(distances)
        best_dist = distances[best_local_idx]
        best_idx = clean_indices[best_local_idx]

        logger.debug(f"Best match distance: {best_dist:.4f} (tolerance: {tolerance})")

        if best_dist <= tolerance:
            return best_idx, best_dist

        logger.debug(f"Best distance {best_dist:.4f} exceeds tolerance {tolerance}")
        return None, None
