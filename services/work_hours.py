from datetime import datetime

def calculate_work_hours(login_time, logout_time):

    total = logout_time - login_time

    hours = total.seconds // 3600
    minutes = (total.seconds % 3600) // 60

    return f"{hours}h {minutes}m"