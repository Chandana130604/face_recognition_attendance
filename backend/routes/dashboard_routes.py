from flask import Blueprint, jsonify
from models.attendance_model import AttendanceModel

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/summary', methods=['GET'])
def summary():
    stats = AttendanceModel.get_attendance_summary()
    return jsonify(stats), 200

@dashboard_bp.route('/recent', methods=['GET'])
def recent():
    # For simplicity, reuse existing recent logic from main; you can implement in model
    from datetime import datetime
    from database.db_connection import attendance_collection, employees_collection
    recent = list(attendance_collection.find(
        {"login_time": {"$ne": None}},
        {"_id": 0, "employee_id": 1, "login_time": 1, "logout_time": 1}
    ).sort("login_time", -1).limit(5))
    result = []
    for rec in recent:
        emp = employees_collection.find_one({"employee_id": rec['employee_id']}, {"name": 1})
        name = emp['name'] if emp else "Unknown"
        action = "logged in" if not rec.get('logout_time') else "logged out"
        time = rec['login_time'].strftime("%H:%M") if rec.get('login_time') else ""
        result.append({
            "employee_name": name,
            "action": action,
            "time": time
        })
    return jsonify(result), 200