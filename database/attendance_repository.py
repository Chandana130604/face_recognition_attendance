from database.mongodb_connection import Database
from models.attendance import Attendance
from datetime import datetime, timedelta
from typing import List, Optional

class AttendanceRepository:
    def __init__(self):
        self.collection = Database().get_collection("attendance")
        # Ensure unique index on emp_id + date to prevent duplicates
        self.collection.create_index([("emp_id", 1), ("date", 1)], unique=True)

    def upsert(self, attendance: Attendance) -> str:
        """
        Insert or update an attendance record for a given employee and date.
        Returns the inserted/updated document's _id as a string.
        """
        filter_query = {
            "emp_id": attendance.emp_id,
            "date": attendance.date
        }
        update_data = {
            "$set": {
                "name": attendance.name,
                "login_time": attendance.login_time,
                "logout_time": attendance.logout_time,
                "status": attendance.status
            }
        }
        result = self.collection.update_one(filter_query, update_data, upsert=True)
        if result.upserted_id:
            return str(result.upserted_id)
        # If updated, fetch the existing document's _id
        doc = self.collection.find_one(filter_query)
        return str(doc["_id"]) if doc else None

    def find_by_emp_id_and_date(self, emp_id: str, date: str) -> Optional[Attendance]:
        """Find attendance for a specific employee on a specific date."""
        doc = self.collection.find_one({"emp_id": emp_id, "date": date})
        if doc:
            return Attendance(
                _id=str(doc["_id"]),
                emp_id=doc["emp_id"],
                name=doc["name"],
                date=doc["date"],
                login_time=doc.get("login_time"),
                logout_time=doc.get("logout_time"),
                status=doc.get("status", "Absent")
            )
        return None

    def find_recent_by_emp_id(self, emp_id: str, hours: int = 24) -> Optional[Attendance]:
        """Find the most recent attendance for an employee within the last 'hours'."""
        cutoff = datetime.now() - timedelta(hours=hours)
        doc = self.collection.find_one({
            "emp_id": emp_id,
            "login_time": {"$gte": cutoff}
        }, sort=[("login_time", -1)])
        if doc:
            return Attendance(
                _id=str(doc["_id"]),
                emp_id=doc["emp_id"],
                name=doc["name"],
                date=doc["date"],
                login_time=doc.get("login_time"),
                logout_time=doc.get("logout_time"),
                status=doc.get("status", "Absent")
            )
        return None

    def find_by_date(self, date: str) -> List[Attendance]:
        """Return all attendance records for a specific date."""
        records = []
        for doc in self.collection.find({"date": date}):
            records.append(Attendance(
                _id=str(doc["_id"]),
                emp_id=doc["emp_id"],
                name=doc["name"],
                date=doc["date"],
                login_time=doc.get("login_time"),
                logout_time=doc.get("logout_time"),
                status=doc.get("status", "Absent")
            ))
        return records

    def find_by_date_range(self, start_date: str, end_date: str) -> List[Attendance]:
        """
        Return all attendance records with date between start_date and end_date (inclusive).
        Sorted by date ascending (oldest first).
        """
        records = []
        for doc in self.collection.find(
            {"date": {"$gte": start_date, "$lte": end_date}}
        ).sort("date", 1):
            records.append(Attendance(
                _id=str(doc["_id"]),
                emp_id=doc["emp_id"],
                name=doc["name"],
                date=doc["date"],
                login_time=doc.get("login_time"),
                logout_time=doc.get("logout_time"),
                status=doc.get("status", "Absent")
            ))
        return records