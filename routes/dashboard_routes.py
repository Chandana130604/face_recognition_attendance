from flask import Blueprint, jsonify, current_app
from services.dashboard_service import DashboardService

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

@dashboard_bp.route('/stats', methods=['GET'])
def stats():
    try:
        data = DashboardService.get_stats()
        return jsonify(data)
    except Exception as e:
        current_app.logger.error(f"Error in /stats: {e}")
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/recent-activity', methods=['GET'])
def recent_activity():
    try:
        data = DashboardService.get_recent_activity()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/attendance-analytics', methods=['GET'])
def attendance_analytics():
    try:
        data = DashboardService.get_attendance_analytics()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/daily-attendance', methods=['GET'])
def daily_attendance():
    # For chart: last 7 days
    try:
        # You would query the database; here we return dummy data
        labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        present = [42, 38, 45, 44, 40, 20, 0]
        absent = [8, 12, 5, 6, 10, 30, 50]
        late = [2, 3, 1, 2, 1, 0, 0]
        return jsonify({'labels': labels, 'present': present, 'absent': absent, 'late': late})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/weekly-trends', methods=['GET'])
def weekly_trends():
    try:
        labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
        data = [180, 195, 210, 200]
        return jsonify({'labels': labels, 'attendance': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/alerts', methods=['GET'])
def alerts():
    # In a real system, you would fetch from an alerts collection.
    # Here we return static examples.
    alerts = [
        "Unknown face detected at 09:15 AM",
        "Rahul marked login at 09:02 AM",
        "John is late (09:30 AM)"
    ]
    return jsonify(alerts)