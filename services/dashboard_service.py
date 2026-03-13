from models.employee_model import EmployeeModel
from models.attendance_model import AttendanceModel
from services.attendance_service import get_attendance_analytics

class DashboardService:
    @staticmethod
    def get_stats():
        return AttendanceModel.get_today_stats()

    @staticmethod
    def get_recent_activity():
        return AttendanceModel.get_recent_activity()

    @staticmethod
    def get_attendance_analytics():
        # Reuse existing analytics logic (from analytics service)
        from services.analytics_service import AnalyticsService
        return AnalyticsService.get_summary()