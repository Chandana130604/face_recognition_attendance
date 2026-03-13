from models.settings_model import SettingsModel
from datetime import datetime

class AttendanceService:
    @staticmethod
    def apply_rules(emp_id, login_time):
        # Fetch settings from database (or use defaults)
        settings_doc = SettingsModel.get_settings()
        if settings_doc:
            # Remove _id field if present
            settings = {k: v for k, v in settings_doc.items() if k != "_id"}
        else:
            settings = SettingsModel.get_defaults()

        # Convert times to comparable format
        login_str = login_time.strftime("%H:%M")
        if login_str > settings["late_threshold"]:
            return "late"
        return "present"