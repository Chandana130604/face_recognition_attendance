from datetime import datetime
from database import attendance

def mark_attendance(emp_id):
    """
    Marks login for the employee if not already logged in today.
    Returns a status message.
    """
    today = datetime.now().strftime("%Y-%m-%d")

    existing = attendance.find_one({
        "emp_id": emp_id,
        "date": today
    })

    if existing:
        return "Attendance already marked"

    login_time = datetime.now()

    attendance.insert_one({
        "emp_id": emp_id,
        "date": today,
        "login_time": login_time,
        "logout_time": None
    })

    return "Login Recorded"