from database.mongodb_connection import Database
from datetime import datetime
import csv
import os

class AttendanceManager:
    def __init__(self):
        self.db = Database()
        self.collection = self.db.get_collection('attendance')
        # Ensure unique index on employee_id + date
        self.collection.create_index([('employee_id', 1), ('date', 1)], unique=True)

    def check_in(self, employee_id):
        """Mark check-in for an employee today."""
        today = datetime.now().strftime('%Y-%m-%d')
        now = datetime.now()
        doc = self.collection.find_one({'employee_id': employee_id, 'date': today})
        if not doc:
            self.collection.insert_one({
                'employee_id': employee_id,
                'date': today,
                'check_in_time': now,
                'check_out_time': None,
                'status': 'Present'
            })
            return True
        return False

    def check_out(self, employee_id):
        """Mark check-out for an employee today (if already checked in)."""
        today = datetime.now().strftime('%Y-%m-%d')
        now = datetime.now()
        result = self.collection.update_one(
            {'employee_id': employee_id, 'date': today},
            {'$set': {'check_out_time': now}}
        )
        return result.modified_count > 0

    def get_today_attendance(self, employee_id):
        """Return today's attendance record for a given employee."""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.collection.find_one({'employee_id': employee_id, 'date': today})

    def get_daily_attendance(self, date_str):
        """Return all attendance records for a specific date."""
        return list(self.collection.find({'date': date_str}, {'_id': 0}))

    def get_attendance_range(self, start_date, end_date):
        """Return attendance records between start_date and end_date (inclusive)."""
        return list(self.collection.find(
            {'date': {'$gte': start_date, '$lte': end_date}},
            {'_id': 0}
        ).sort('date', 1))

    def get_employee_attendance(self, employee_id, start_date, end_date):
        """
        Return attendance records for a specific employee over a date range.
        """
        return list(self.collection.find(
            {'employee_id': employee_id, 'date': {'$gte': start_date, '$lte': end_date}},
            {'_id': 0}
        ).sort('date', 1))

    def export_to_csv(self, date_str, filepath):
        """Export attendance for a given date to a CSV file."""
        records = self.get_daily_attendance(date_str)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Employee ID', 'Date', 'Check In', 'Check Out', 'Status'])
            for r in records:
                check_in = r.get('check_in_time', '')
                if check_in:
                    check_in = check_in.strftime('%H:%M:%S') if isinstance(check_in, datetime) else check_in
                check_out = r.get('check_out_time', '')
                if check_out:
                    check_out = check_out.strftime('%H:%M:%S') if isinstance(check_out, datetime) else check_out
                writer.writerow([
                    r.get('employee_id', ''),
                    r.get('date', ''),
                    check_in,
                    check_out,
                    r.get('status', '')
                ])
        return filepath