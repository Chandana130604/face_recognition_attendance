import cv2
import numpy as np

def get_face_encoding(face_image):
    """
    Resizes the cropped face to 100x100 and flattens it into a 1D array.
    This is a simple placeholder; replace with a real face recognition model if needed.
    """
    face_image = cv2.resize(face_image, (100, 100))
    encoding = face_image.flatten()
    return encoding