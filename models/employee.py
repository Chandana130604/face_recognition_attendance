from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Employee:
    emp_id: str
    name: str
    department: str
    email: str
    role: str                     # e.g., "employee", "manager", "hr", "supervisor"
    face_encodings: List[List[float]]
    created_at: Optional[datetime] = None
    _id: Optional[str] = None