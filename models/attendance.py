from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Attendance:
    employee_id: str
    date: str
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    status: str = "Present"
    _id: Optional[str] = None