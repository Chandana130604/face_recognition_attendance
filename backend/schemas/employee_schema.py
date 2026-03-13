from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class EmployeeBase(BaseModel):
    employee_id: str
    name: str
    department: str
    email: EmailStr
    phone: Optional[str] = None
    status: str = "Active"
    joining_date: Optional[date] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    status: Optional[str] = None

class EmployeeResponse(EmployeeBase):
    id: int
    attendance_percent: Optional[float] = None  # computed later

    class Config:
        from_attributes = True

class EmployeeListResponse(BaseModel):
    total: int
    page: int
    limit: int
    employees: list[EmployeeResponse]