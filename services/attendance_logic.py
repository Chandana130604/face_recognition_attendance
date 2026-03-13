from datetime import datetime

def get_attendance_status(login_time):

    office_start = login_time.replace(hour=9, minute=0, second=0)
    late_time = login_time.replace(hour=9, minute=15, second=0)

    if login_time <= office_start:
        return "Present"

    elif login_time <= late_time:
        return "Late"

    else:
        return "Absent"