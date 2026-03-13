from models.settings_model import SettingsModel

DEFAULTS = {
    "office_start_time": "09:00",
    "late_threshold": "09:15",
    "half_day_threshold": "13:00",
    "camera_source": "Default Camera",
    "detection_sensitivity": 70,
    "theme": "Light",
    "notifications": True
}

class SettingsService:
    @staticmethod
    def get_current():
        """Return current settings (merged with defaults if any missing)."""
        doc = SettingsModel.get_settings()
        if doc:
            # Remove _id and updated_at before returning
            doc.pop("_id", None)
            doc.pop("updated_at", None)
            # Merge with defaults (doc values override defaults)
            return {**DEFAULTS, **doc}
        else:
            return DEFAULTS.copy()

    @staticmethod
    def save(settings):
        """Validate and save settings."""
        # Basic validation: ensure required fields exist
        required = ["office_start_time", "late_threshold", "half_day_threshold",
                    "camera_source", "detection_sensitivity", "theme", "notifications"]
        for field in required:
            if field not in settings:
                return {"success": False, "error": f"Missing field: {field}"}
        # Ensure sensitivity is integer
        settings["detection_sensitivity"] = int(settings["detection_sensitivity"])
        SettingsModel.update_settings(settings)
        return {"success": True, "message": "Settings updated"}