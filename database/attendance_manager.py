from database.mongodb_connection import Database
from datetime import datetime, date
import csv
import os

class AttendanceManager:
    def __init__(self):
        self.db = Database()
        self.collection = self.db.get_collection('attendance')
        self.collection.create_index([('emp_id', 1), ('date', 1)], unique=True)

    def mark_login(self, emp_id, name, login_time=None):
        if login_time is None:
            login_time = datetime.now()
        date_str = login_time.strftime('%Y-%m-%d')
        doc = self.collection.find_one({'emp_id': emp_id, 'date': date_str})
        if doc:
            if not doc.get('login_time'):
                self.collection.update_one(
                    {'_id': doc['_id']},
                    {'$set': {'login_time': login_time, 'status': 'Present'}}
                )
        else:
            self.collection.insert_one({
                'emp_id': emp_id,
                'name': name,
                'date': date_str,
                'login_time': login_time,
                'logout_time': None,
                'status': 'Present'
            })

    def mark_logout(self, emp_id, logout_time=None):
        if logout_time is None:
            logout_time = datetime.now()
        date_str = logout_time.strftime('%Y-%m-%d')
        doc = self.collection.find_one({'emp_id': emp_id, 'date': date_str})
        if doc and doc.get('login_time'):
            self.collection.update_one(
                {'_id': doc['_id']},
                {'$set': {'logout_time': logout_time}}
            )

    def get_daily_attendance(self, date_str):
        return list(self.collection.find({'date': date_str}, {'_id': 0}))

    def get_attendance_range(self, start_date, end_date):
        """
        Return attendance records for a range of dates (inclusive).
        Results sorted by date ascending.
        """
        return list(self.collection.find(
            {"date": {"$gte": start_date, "$lte": end_date}},
            {"_id": 0}
        ).sort("date", 1))

    def export_to_csv(self, date_str, filepath):
        records = self.get_daily_attendance(date_str)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Employee ID', 'Name', 'Login Time', 'Logout Time', 'Status'])
            for r in records:
                login = r['login_time'].strftime('%H:%M:%S') if r.get('login_time') else ''
                logout = r['logout_time'].strftime('%H:%M:%S') if r.get('logout_time') else ''
                writer.writerow([r['emp_id'], r['name'], login, logout, r.get('status', '')])
        return filepath