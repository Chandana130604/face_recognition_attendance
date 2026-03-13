from database.db_connection import employees_collection, attendance_collection
from datetime import datetime, timedelta

class AttendanceModel:
    @staticmethod
    def mark_login(emp_id, login_time=None):
        today = datetime.now().strftime("%Y-%m-%d")
        if login_time is None:
            login_time = datetime.now()
        existing = attendance_collection.find_one({"employee_id": emp_id, "date": today})
        if existing:
            return {"success": False, "message": "Already logged in today"}
        doc = {
            "employee_id": emp_id,
            "date": today,
            "login_time": login_time,
            "logout_time": None,
            "status": "present",
            "late_flag": False,
            "created_at": datetime.now()
        }
        attendance_collection.insert_one(doc)
        return {"success": True, "message": "Login recorded"}

    @staticmethod
    def mark_logout(emp_id, logout_time=None):
        today = datetime.now().strftime("%Y-%m-%d")
        if logout_time is None:
            logout_time = datetime.now()
        record = attendance_collection.find_one({"employee_id": emp_id, "date": today})
        if not record:
            return {"success": False, "message": "No login record found"}
        if record.get("logout_time"):
            return {"success": False, "message": "Already logged out"}
        attendance_collection.update_one(
            {"_id": record["_id"]},
            {"$set": {"logout_time": logout_time}}
        )
        return {"success": True, "message": "Logout recorded"}

    @staticmethod
    def get_today_attendance():
        today = datetime.now().strftime("%Y-%m-%d")
        records = list(attendance_collection.find({"date": today}, {"_id": 0}))
        for rec in records:
            emp = employees_collection.find_one({"employee_id": rec["employee_id"]}, {"name": 1})
            rec["employee_name"] = emp["name"] if emp else "Unknown"
            if rec.get("login_time"):
                rec["login_time"] = rec["login_time"].strftime("%H:%M")
            if rec.get("logout_time"):
                rec["logout_time"] = rec["logout_time"].strftime("%H:%M")
        return records

    @staticmethod
    def get_employee_attendance(emp_id, days=30):
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        return list(attendance_collection.find(
            {"employee_id": emp_id, "date": {"$gte": start_date}},
            {"_id": 0}
        ).sort("date", -1))

    @staticmethod
    def get_today_stats():
        total = employees_collection.count_documents({})
        today = datetime.now().strftime("%Y-%m-%d")
        present = attendance_collection.count_documents({"date": today, "status": "present"})
        absent = total - present
        late = attendance_collection.count_documents({"date": today, "late_flag": True})
        return {
            "total_employees": total,
            "present_today": present,
            "absent_today": absent,
            "late_entries": late
        }

    @staticmethod
    def get_attendance_summary():
        total = employees_collection.count_documents({})
        today = datetime.now().strftime("%Y-%m-%d")
        present = attendance_collection.count_documents({"date": today, "status": "present"})
        absent = total - present
        late = attendance_collection.count_documents({"date": today, "late_flag": True})
        first_day = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        new_this_month = employees_collection.count_documents({"created_at": {"$gte": first_day}})
        attendance_percentage = round((present / total) * 100, 1) if total else 0
        return {
            "total_employees": total,
            "active_employees": total,
            "present_today": present,
            "absent_today": absent,
            "late_employees": late,
            "new_employees_this_month": new_this_month,
            "attendance_percentage": attendance_percentage
        }