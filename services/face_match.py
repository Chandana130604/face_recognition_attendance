import face_recognition
import numpy as np

def match_face(encoding, known_encodings, emp_ids):

    matches = face_recognition.compare_faces(
        known_encodings,
        encoding,
        tolerance=0.5
    )

    if True in matches:

        index = matches.index(True)

        return emp_ids[index]

    return None