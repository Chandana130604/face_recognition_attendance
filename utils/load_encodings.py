import numpy as np
from database import employees

def load_known_faces():

    encodings = []
    ids = []

    for emp in employees.find():

        encodings.append(np.array(emp["encoding"]))
        ids.append(emp["emp_id"])

    return encodings, ids