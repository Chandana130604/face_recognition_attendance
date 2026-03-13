from flask import Blueprint, request, jsonify
from models.employee_model import EmployeeModel

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/', methods=['GET'])
def list_employees():
    try:
        employees = EmployeeModel.get_all_employees()
        # Remove face_encoding from response
        for emp in employees:
            emp.pop('face_encoding', None)
        return jsonify(employees), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@employee_bp.route('/', methods=['POST'])
def add_employee():
    data = request.json
    required = ['emp_id', 'name', 'email', 'department']
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400
    result = EmployeeModel.add_employee(
        emp_id=data['emp_id'],
        name=data['name'],
        email=data['email'],
        department=data['department'],
        phone=data.get('phone'),
        status=data.get('status', 'Active')
    )
    if result['success']:
        return jsonify(result), 201
    return jsonify(result), 400

@employee_bp.route('/<emp_id>', methods=['GET'])
def get_employee(emp_id):
    emp = EmployeeModel.get_employee_by_id(emp_id)
    if emp:
        return jsonify(emp), 200
    return jsonify({"error": "Not found"}), 404

@employee_bp.route('/<emp_id>', methods=['PUT'])
def update_employee(emp_id):
    data = request.json
    result = EmployeeModel.update_employee(emp_id, data)
    return jsonify(result), 200 if result['success'] else 404

@employee_bp.route('/<emp_id>', methods=['DELETE'])
def delete_employee(emp_id):
    result = EmployeeModel.delete_employee(emp_id)
    return jsonify(result), 200 if result['success'] else 404

@employee_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').lower()
    employees = EmployeeModel.get_all_employees()
    filtered = [e for e in employees if query in e['name'].lower() or query in e['employee_id'].lower()]
    return jsonify(filtered), 200

@employee_bp.route('/filter', methods=['GET'])
def filter_by_department():
    dept = request.args.get('department', '')
    employees = EmployeeModel.get_all_employees()
    filtered = [e for e in employees if e['department'] == dept] if dept else employees
    return jsonify(filtered), 200