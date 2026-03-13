from database import attendance_collection, employees_collection
from datetime import datetime

def get_report_data(report_type, start_date, end_date, department=None, employee=None):
    """
    Fetch attendance records with optional filters.
    Returns a list of dicts with keys: employee, id, department, date, login, logout, status.
    """
    query = {}
    if start_date and end_date:
        query['date'] = {'$gte': start_date, '$lte': end_date}
    if employee:
        query['employee_id'] = employee
    elif department:
        # Get all employees in that department
        emp_ids = [e['employee_id'] for e in employees_collection.find({'department': department})]
        query['employee_id'] = {'$in': emp_ids}

    records = list(attendance_collection.find(query, {'_id': 0}).sort('date', -1))

    result = []
    for rec in records:
        emp = employees_collection.find_one({'employee_id': rec['employee_id']}, {'_id': 0, 'name': 1, 'department': 1})
        if not emp:
            continue
        result.append({
            'employee': emp['name'],
            'id': rec['employee_id'],
            'department': emp['department'],
            'date': rec['date'],
            'login': rec.get('login_time', '').strftime('%H:%M') if rec.get('login_time') else '',
            'logout': rec.get('logout_time', '').strftime('%H:%M') if rec.get('logout_time') else '',
            'status': rec.get('status', '').capitalize()
        })
    return result