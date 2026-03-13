from database.db_connection import employees_collection
from datetime import datetime

class EmployeeModel:
    @staticmethod
    def add_employee(emp_id, name, email, department, face_encoding=None, phone=None, status="Active"):
        if employees_collection.find_one({"employee_id": emp_id}):
            return {"success": False, "message": "Employee ID already exists"}
        doc = {
            "employee_id": emp_id,
            "name": name,
            "email": email,
            "department": department,
            "phone": phone,
            "status": status,
            "face_encoding": face_encoding.tolist() if face_encoding is not None else None,
            "created_at": datetime.now()
        }
        employees_collection.insert_one(doc)
        return {"success": True, "message": "Employee added"}

    @staticmethod
    def get_all_employees():
        return list(employees_collection.find({}, {"_id": 0}))

    @staticmethod
    def get_employee_by_id(emp_id):
        return employees_collection.find_one({"employee_id": emp_id}, {"_id": 0})

    @staticmethod
    def update_employee(emp_id, update_data):
        update_data.pop('_id', None)
        update_data.pop('employee_id', None)
        result = employees_collection.update_one(
            {"employee_id": emp_id},
            {"$set": update_data}
        )
        return {"success": result.matched_count > 0, "message": "Updated" if result.matched_count else "Not found"}

    @staticmethod
    def delete_employee(emp_id):
        result = employees_collection.delete_one({"employee_id": emp_id})
        return {"success": result.deleted_count > 0}

    @staticmethod
    def get_all_face_encodings():
        return list(employees_collection.find(
            {"face_encoding": {"$ne": None}},
            {"_id": 0, "employee_id": 1, "name": 1, "face_encoding": 1}
        ))