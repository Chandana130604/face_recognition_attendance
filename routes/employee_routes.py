from flask import Blueprint, jsonify
from database.db_connection import employees_collection  # import the collection

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/', methods=['GET'])
def list_employees():
    try:
        # Fetch all employees, exclude MongoDB '_id' field (not JSON serializable)
        employees = list(employees_collection.find({}, {"_id": 0}))
        return jsonify(employees), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500