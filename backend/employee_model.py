from database import employees_collection
from datetime import datetime

class EmployeeModel:
    @staticmethod
    def add_employee(emp_id, name, email, department, phone=None, face_encoding=None, status="Active"):
        """Insert a new employee."""
        if employees_collection.find_one({"employee_id": emp_id}):
            return {"success": False, "message": "Employee ID already exists"}
        doc = {
            "employee_id": emp_id,
            "name": name,
            "email": email,
            "department": department,
            "phone": phone,
            "face_encoding": face_encoding.tolist() if face_encoding is not None else None,
            "attendance_percentage": 0.0,
            "status": status,
            "created_at": datetime.now()
        }
        employees_collection.insert_one(doc)
        return {"success": True, "message": "Employee added", "employee_id": emp_id}

    @staticmethod
    def get_all_employees():
        """Return all employees (excluding face_encoding)."""
        return list(employees_collection.find({}, {"_id": 0, "face_encoding": 0}))

    @staticmethod
    def get_employee_by_id(emp_id):
        """Return a single employee (including face_encoding for internal use)."""
        return employees_collection.find_one({"employee_id": emp_id}, {"_id": 0})

    @staticmethod
    def update_employee(emp_id, update_data):
        """Update employee details. update_data can contain any fields."""
        # Prevent updating the primary key
        update_data.pop('employee_id', None)
        update_data.pop('_id', None)
        result = employees_collection.update_one(
            {"employee_id": emp_id},
            {"$set": update_data}
        )
        if result.matched_count:
            return {"success": True, "message": "Employee updated"}
        return {"success": False, "message": "Employee not found"}

    @staticmethod
    def delete_employee(emp_id):
        result = employees_collection.delete_one({"employee_id": emp_id})
        if result.deleted_count:
            return {"success": True, "message": "Employee deleted"}
        return {"success": False, "message": "Employee not found"}

    @staticmethod
    def update_face_encoding(emp_id, face_encoding):
        result = employees_collection.update_one(
            {"employee_id": emp_id},
            {"$set": {"face_encoding": face_encoding.tolist()}}
        )
        if result.matched_count:
            return {"success": True, "message": "Face encoding updated"}
        return {"success": False, "message": "Employee not found"}

    @staticmethod
    def get_all_face_encodings():
        """Used by recognition endpoint."""
        return list(employees_collection.find(
            {"face_encoding": {"$ne": None}},
            {"_id": 0, "employee_id": 1, "name": 1, "face_encoding": 1}
        ))