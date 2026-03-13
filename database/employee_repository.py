from database.mongodb_connection import Database
from models.employee import Employee
from datetime import datetime
from typing import List, Optional
from pymongo.errors import DuplicateKeyError

class EmployeeRepository:
    def __init__(self):
        self.collection = Database().get_collection("employees")
        self.collection.create_index("emp_id", unique=True)

    def insert(self, employee: Employee) -> str:
        emp_dict = {
            "emp_id": employee.emp_id,
            "name": employee.name,
            "department": employee.department,
            "email": employee.email,
            "role": employee.role,
            "face_encodings": employee.face_encodings,
            "created_at": employee.created_at or datetime.now()
        }
        result = self.collection.insert_one(emp_dict)
        return str(result.inserted_id)

    def find_by_emp_id(self, emp_id: str) -> Optional[Employee]:
        doc = self.collection.find_one({"emp_id": emp_id})
        if doc:
            return Employee(
                _id=str(doc["_id"]),
                emp_id=doc["emp_id"],
                name=doc["name"],
                department=doc.get("department", ""),
                email=doc.get("email", ""),
                role=doc.get("role", "employee"),
                face_encodings=doc.get("face_encodings", []),
                created_at=doc.get("created_at")
            )
        return None

    def find_all(self) -> List[Employee]:
        employees = []
        for doc in self.collection.find():
            employees.append(Employee(
                _id=str(doc["_id"]),
                emp_id=doc["emp_id"],
                name=doc["name"],
                department=doc.get("department", ""),
                email=doc.get("email", ""),
                role=doc.get("role", "employee"),
                face_encodings=doc.get("face_encodings", []),
                created_at=doc.get("created_at")
            ))
        return employees

    def update_face_encodings(self, emp_id: str, new_encodings: List[List[float]]) -> bool:
        result = self.collection.update_one(
            {"emp_id": emp_id},
            {"$set": {"face_encodings": new_encodings}}
        )
        return result.modified_count > 0

    def delete(self, emp_id: str) -> bool:
        result = self.collection.delete_one({"emp_id": emp_id})
        return result.deleted_count > 0