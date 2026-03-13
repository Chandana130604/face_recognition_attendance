from database import attendance

def get_employee_history(emp_id):

    records = attendance.find({"emp_id": emp_id})

    history = []

    for r in records:

        history.append({
            "date": r["date"],
            "login": r["login_time"],
            "logout": r["logout_time"]
        })

    return history