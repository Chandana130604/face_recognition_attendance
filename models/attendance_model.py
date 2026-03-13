from database import db
from datetime import datetime

class AttendanceModel:
    collection = db.attendance

    @staticmethod
    def mark_login(emp_id):
        today = datetime.now().strftime('%Y-%m-%d')
        existing = AttendanceModel.collection.find_one({'employee_id': emp_id, 'date': today})
        if existing:
            return {'success': False, 'message': 'Already logged in today'}
        now = datetime.now()
        doc = {
            'employee_id': emp_id,
            'date': today,
            'login_time': now,
            'status': 'present',        # will be updated to 'late' if needed
            'late_flag': False,
            'created_at': now
        }
        AttendanceModel.collection.insert_one(doc)
        return {'success': True, 'message': 'Login recorded'}

    @staticmethod
    def mark_logout(emp_id):
        today = datetime.now().strftime('%Y-%m-%d')
        rec = AttendanceModel.collection.find_one({'employee_id': emp_id, 'date': today})
        if not rec:
            return {'success': False, 'message': 'No login record found'}
        if rec.get('logout_time'):
            return {'success': False, 'message': 'Already logged out'}
        AttendanceModel.collection.update_one(
            {'_id': rec['_id']},
            {'$set': {'logout_time': datetime.now()}}
        )
        return {'success': True, 'message': 'Logout recorded'}

    @staticmethod
    def get_today_stats():
        today = datetime.now().strftime('%Y-%m-%d')
        total = db.employees.count_documents({})
        present = AttendanceModel.collection.count_documents({'date': today, 'status': 'present'})
        absent = total - present
        late = AttendanceModel.collection.count_documents({'date': today, 'late_flag': True})
        return {
            'total_employees': total,
            'present_today': present,
            'absent_today': absent,
            'late_entries': late
        }

    @staticmethod
    def get_recent_activity(limit=5):
        pipeline = [
            {'$match': {'login_time': {'$ne': None}}},
            {'$sort': {'login_time': -1}},
            {'$limit': limit},
            {'$lookup': {
                'from': 'employees',
                'localField': 'employee_id',
                'foreignField': 'employee_id',
                'as': 'emp'
            }},
            {'$unwind': '$emp'},
            {'$project': {
                'employee_name': '$emp.name',
                'action': {'$cond': [{'$eq': ['$logout_time', None]}, 'logged in', 'logged out']},
                'time': {'$dateToString': {'format': '%H:%M', 'date': '$login_time'}},
                'date': 1
            }}
        ]
        return list(AttendanceModel.collection.aggregate(pipeline))