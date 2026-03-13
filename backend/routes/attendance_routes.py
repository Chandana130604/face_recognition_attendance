from flask import Blueprint, request, jsonify
from models.attendance_model import AttendanceModel

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    emp_id = data.get('emp_id')
    if not emp_id:
        return jsonify({"success": False, "error": "emp_id required"}), 400
    result = AttendanceModel.mark_login(emp_id)
    return jsonify(result), 200 if result['success'] else 400

@attendance_bp.route('/logout', methods=['POST'])
def logout():
    data = request.json
    emp_id = data.get('emp_id')
    if not emp_id:
        return jsonify({"success": False, "error": "emp_id required"}), 400
    result = AttendanceModel.mark_logout(emp_id)
    return jsonify(result), 200 if result['success'] else 400

@attendance_bp.route('/today', methods=['GET'])
def today():
    records = AttendanceModel.get_today_attendance()
    return jsonify(records), 200

@attendance_bp.route('/employee/<emp_id>', methods=['GET'])
def employee_attendance(emp_id):
    days = request.args.get('days', default=30, type=int)
    records = AttendanceModel.get_employee_attendance(emp_id, days)
    return jsonify(records), 200