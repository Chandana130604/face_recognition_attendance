from database.employee_repository import EmployeeRepository
from models.employee import Employee
import datetime
from pymongo.errors import DuplicateKeyError
from typing import List, Optional

class EmployeeManager:
    def __init__(self):
        self.repo = EmployeeRepository()

    def add_employee(self, emp_id: str, name: str, department: str, email: str, role: str, encodings: List[List[float]]):
        if self.repo.find_by_emp_id(emp_id):
            raise ValueError(f"Employee with ID {emp_id} already exists.")
        employee = Employee(
            emp_id=emp_id,
            name=name,
            department=department,
            email=email,
            role=role,
            face_encodings=encodings,
            created_at=datetime.datetime.now()
        )
        try:
            return self.repo.insert(employee)
        except DuplicateKeyError:
            raise ValueError(f"Employee with ID {emp_id} already exists.")

    def get_employee(self, emp_id: str) -> Optional[Employee]:
        return self.repo.find_by_emp_id(emp_id)

    def get_employee_by_emp_id(self, emp_id: str) -> Optional[Employee]:
        return self.get_employee(emp_id)

    def get_all_employees(self) -> List[Employee]:
        return self.repo.find_all()

    def update_face_encodings(self, emp_id: str, new_encodings: List[List[float]]):
        existing = self.repo.find_by_emp_id(emp_id)
        if not existing:
            raise ValueError("Employee not found")
        combined = existing.face_encodings + new_encodings
        return self.repo.update_face_encodings(emp_id, combined)

    def update_encoding(self, emp_id: str, encoding: List[float]):
        return self.update_face_encodings(emp_id, [encoding])

    def delete_employee(self, emp_id: str) -> bool:
        return self.repo.delete(emp_id)