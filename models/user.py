from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    username: str           # email or employee ID
    password_hash: str
    role: str                # 'admin' or 'employee'
    employee_id: Optional[str] = None  # if employee, link to employee record
    failed_attempts: int = 0
    locked_until: Optional[datetime] = None
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    _id: Optional[str] = None