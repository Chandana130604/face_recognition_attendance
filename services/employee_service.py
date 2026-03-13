from models.employee_model import EmployeeModel
from database import attendance_collection
from datetime import datetime, timedelta

class EmployeeService:
    @staticmethod
    def compute_attendance_percentage(emp_id, days=30):
        """Calculate attendance percentage for the last `days` days."""
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        total_present = attendance_collection.count_documents({
            "employee_id": emp_id,
            "date": {"$gte": start_date},
            "status": "present"
        })
        return round((total_present / days) * 100, 1) if days > 0 else 0

    @staticmethod
    def enrich_with_attendance(employee_list):
        """Add attendance_percentage to each employee in the list."""
        for emp in employee_list:
            emp['attendance_percentage'] = EmployeeService.compute_attendance_percentage(emp['employee_id'])
        return employee_list

    @staticmethod
    def get_all_with_attendance():
        employees = EmployeeModel.get_all_employees()
        return EmployeeService.enrich_with_attendance(employees)

    @staticmethod
    def search_employees(query):
        """Search by name or employee_id (case‑insensitive partial match)."""
        all_emps = EmployeeModel.get_all_employees()
        query = query.lower()
        filtered = [emp for emp in all_emps if query in emp['name'].lower() or query in emp['employee_id'].lower()]
        return EmployeeService.enrich_with_attendance(filtered)

    @staticmethod
    def filter_by_department(department):
        all_emps = EmployeeModel.get_all_employees()
        filtered = [emp for emp in all_emps if emp['department'].lower() == department.lower()]
        return EmployeeService.enrich_with_attendance(filtered)