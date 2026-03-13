from database import db
from datetime import datetime

SETTINGS_ID = "system_settings"

class SettingsModel:
    @staticmethod
    def get_settings():
        """Return the settings document, or None if not found."""
        return db.settings.find_one({"_id": SETTINGS_ID})

    @staticmethod
    def update_settings(data):
        """Update or insert settings document."""
        data["updated_at"] = datetime.now()
        result = db.settings.update_one(
            {"_id": SETTINGS_ID},
            {"$set": data},
            upsert=True
        )
        return result.modified_count > 0 or result.upserted_id is not None