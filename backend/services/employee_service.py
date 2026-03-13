# (Optional) Could contain methods for bulk operations, validation, etc.from sqlalchemy.orm import Session
from models.employee_model import Employee
from schemas.employee_schema import EmployeeCreate, EmployeeUpdate
from datetime import datetime, timedelta
import json
import pandas as pd
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class EmployeeService:
    @staticmethod
    def get_attendance_percentage(employee_id: str, db: Session) -> float:
        # Placeholder: you would query the attendance table
        # For now, return a random percentage for demonstration.
        # In real implementation, count present days over last 30 days.
        # Example: present = db.query(Attendance).filter(...).count()
        # return (present / 30) * 100
        return 0.0  # Replace with actual calculation

    @staticmethod
    def create_employee(db: Session, emp_data: EmployeeCreate):
        db_emp = Employee(**emp_data.dict())
        db.add(db_emp)
        db.commit()
        db.refresh(db_emp)
        return db_emp

    @staticmethod
    def get_employee(db: Session, emp_id: int):
        return db.query(Employee).filter(Employee.id == emp_id).first()

    @staticmethod
    def get_employee_by_employee_id(db: Session, employee_id: str):
        return db.query(Employee).filter(Employee.employee_id == employee_id).first()

    @staticmethod
    def update_employee(db: Session, emp_id: int, emp_data: EmployeeUpdate):
        db_emp = db.query(Employee).filter(Employee.id == emp_id).first()
        if db_emp:
            for key, value in emp_data.dict(exclude_unset=True).items():
                setattr(db_emp, key, value)
            db.commit()
            db.refresh(db_emp)
        return db_emp

    @staticmethod
    def delete_employee(db: Session, emp_id: int):
        db_emp = db.query(Employee).filter(Employee.id == emp_id).first()
        if db_emp:
            db.delete(db_emp)
            db.commit()
            return True
        return False

    @staticmethod
    def get_employees_paginated(db: Session, page: int, limit: int, department: str = None, search: str = None):
        query = db.query(Employee)
        if department:
            query = query.filter(Employee.department == department)
        if search:
            query = query.filter(
                (Employee.name.ilike(f"%{search}%")) | (Employee.employee_id.ilike(f"%{search}%"))
            )
        total = query.count()
        employees = query.offset((page - 1) * limit).limit(limit).all()
        return total, employees

    @staticmethod
    def import_from_csv(file_content: bytes):
        df = pd.read_csv(io.BytesIO(file_content))
        # Expected columns: employee_id, name, department, email, phone
        required = ['employee_id', 'name', 'department', 'email', 'phone']
        if not all(col in df.columns for col in required):
            raise ValueError("CSV missing required columns")
        # Convert to list of dicts
        records = df.to_dict(orient='records')
        return records

    @staticmethod
    def import_from_excel(file_content: bytes):
        df = pd.read_excel(io.BytesIO(file_content))
        required = ['employee_id', 'name', 'department', 'email', 'phone']
        if not all(col in df.columns for col in required):
            raise ValueError("Excel missing required columns")
        records = df.to_dict(orient='records')
        return records

    @staticmethod
    def export_to_csv(employees: list):
        df = pd.DataFrame([e.__dict__ for e in employees])
        # Remove SQLAlchemy internal state
        df = df[['employee_id', 'name', 'department', 'email', 'phone', 'status']]
        output = io.StringIO()
        df.to_csv(output, index=False)
        return output.getvalue().encode('utf-8')

    @staticmethod
    def export_to_excel(employees: list):
        df = pd.DataFrame([e.__dict__ for e in employees])
        df = df[['employee_id', 'name', 'department', 'email', 'phone', 'status']]
        output = io.BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        return output.read()

    @staticmethod
    def export_to_pdf(employees: list):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Employee List")
        c.setFont("Helvetica", 10)
        y = height - 80
        c.drawString(50, y, "ID")
        c.drawString(100, y, "Name")
        c.drawString(200, y, "Dept")
        c.drawString(300, y, "Email")
        c.drawString(450, y, "Phone")
        y -= 15
        for emp in employees:
            c.drawString(50, y, emp.employee_id)
            c.drawString(100, y, emp.name[:15])
            c.drawString(200, y, emp.department)
            c.drawString(300, y, emp.email)
            c.drawString(450, y, emp.phone)
            y -= 15
            if y < 50:
                c.showPage()
                y = height - 50
        c.save()
        buffer.seek(0)
        return buffer.read()