import streamlit as st
import cv2
import numpy as np
from PIL import Image
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python.vision import FaceDetector, FaceDetectorOptions, RunningMode
from database import employees, attendance
from services.attendance_service import mark_attendance
from utils.face_encoding import get_face_encoding
from datetime import datetime

# ------------------------------------------------------------
# Initialize MediaPipe detector (cached)
# ------------------------------------------------------------
@st.cache_resource
def load_detector():
    MODEL_PATH = 'blaze_face_short_range.tflite'
    base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
    options = FaceDetectorOptions(
        base_options=base_options,
        running_mode=RunningMode.IMAGE,
        min_detection_confidence=0.5
    )
    return FaceDetector.create_from_options(options)

detector = load_detector()

# ------------------------------------------------------------
# Helper functions (similar to streamlit_helpers.py)
# ------------------------------------------------------------
@st.cache_resource
def load_known_faces():
    known = []
    ids = []
    for emp in employees.find():
        known.append(np.array(emp["encoding"]))
        ids.append(emp["emp_id"])
    return known, ids

def register_face(frame, emp_id, name):
    try:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        detection_result = detector.detect(mp_image)

        if not detection_result.detections:
            return False, "No face detected"

        detection = detection_result.detections[0]
        bbox = detection.bounding_box
        h, w, _ = frame.shape
        x1 = max(0, bbox.origin_x)
        y1 = max(0, bbox.origin_y)
        x2 = min(w, bbox.origin_x + bbox.width)
        y2 = min(h, bbox.origin_y + bbox.height)

        if x2 <= x1 or y2 <= y1:
            return False, "Invalid face crop"

        face_crop = frame[y1:y2, x1:x2]
        encoding = get_face_encoding(face_crop)

        if employees.find_one({"emp_id": emp_id}):
            return False, "Employee ID already exists"

        employees.insert_one({
            "emp_id": emp_id,
            "name": name,
            "encoding": encoding.tolist()
        })
        return True, f"Employee {name} registered successfully"
    except Exception as e:
        return False, f"Error: {str(e)}"

def recognize_face(frame):
    try:
        known_encodings, emp_ids = load_known_faces()
        if not known_encodings:
            return False, "No employees registered", None

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        detection_result = detector.detect(mp_image)

        if not detection_result.detections:
            return False, "No face detected", None

        detection = detection_result.detections[0]
        bbox = detection.bounding_box
        h, w, _ = frame.shape
        x1 = max(0, bbox.origin_x)
        y1 = max(0, bbox.origin_y)
        x2 = min(w, bbox.origin_x + bbox.width)
        y2 = min(h, bbox.origin_y + bbox.height)

        if x2 <= x1 or y2 <= y1:
            return False, "Invalid face crop", None

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
            return True, result, best_match
        else:
            return False, "No matching employee found", None
    except Exception as e:
        return False, f"Error: {str(e)}", None

# ------------------------------------------------------------
# Streamlit UI
# ------------------------------------------------------------
st.set_page_config(page_title="Face Attendance System", layout="wide")
st.title("📸 Face Attendance System")

menu = st.sidebar.selectbox("Menu", ["Home", "Register Employee", "Mark Attendance", "View Attendance"])

if menu == "Home":
    st.write("## Welcome")
    st.markdown("""
    This system uses face recognition to mark attendance.
    - **Register Employee**: Add new employees with their face data.
    - **Mark Attendance**: Recognize faces and record login time.
    - **View Attendance**: See today's attendance records.
    """)

elif menu == "Register Employee":
    st.header("Register New Employee")
    col1, col2 = st.columns(2)

    with col1:
        emp_id = st.text_input("Employee ID")
        name = st.text_input("Employee Name")
        img_file = st.camera_input("Capture Face")

        if img_file and emp_id and name:
            # Convert to OpenCV format
            bytes_data = img_file.getvalue()
            nparr = np.frombuffer(bytes_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            success, message = register_face(frame, emp_id, name)
            if success:
                st.success(message)
            else:
                st.error(message)

    with col2:
        st.subheader("Registered Employees")
        for emp in employees.find({}, {"_id": 0, "emp_id": 1, "name": 1}):
            st.write(f"- {emp['emp_id']}: {emp['name']}")

elif menu == "Mark Attendance":
    st.header("Mark Attendance")
    col1, col2 = st.columns(2)

    with col1:
        img_file = st.camera_input("Look at Camera")

        if img_file:
            bytes_data = img_file.getvalue()
            nparr = np.frombuffer(bytes_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            success, message, emp_id = recognize_face(frame)
            if success:
                st.success(f"✅ {emp_id}: {message}")
            else:
                st.warning(message)

    with col2:
        st.subheader("Today's Attendance")
        today = datetime.now().strftime("%Y-%m-%d")
        records = attendance.find({"date": today})
        for record in records:
            login_time = record.get("login_time")
            if login_time:
                time_str = login_time.strftime("%H:%M:%S")
            else:
                time_str = "N/A"
            st.write(f"- {record['emp_id']}: {time_str}")

elif menu == "View Attendance":
    st.header("Attendance Records")
    date_input = st.date_input("Select Date", datetime.now())
    date_str = date_input.strftime("%Y-%m-%d")

    records = attendance.find({"date": date_str})
    if records:
        for record in records:
            login_time = record.get("login_time")
            time_str = login_time.strftime("%H:%M:%S") if login_time else "N/A"
            st.write(f"**{record['emp_id']}** - Login: {time_str}")
    else:
        st.info("No attendance records for this date.")