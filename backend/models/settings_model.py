from database.db_connection import settings_collection

class SettingsModel:
    SETTINGS_ID = "system_settings"

    @staticmethod
    def get_settings():
        return settings_collection.find_one({"_id": SettingsModel.SETTINGS_ID})

    @staticmethod
    def get_defaults():
        return {
            "office_start": "09:00",
            "late_threshold": "09:15",
            "half_day_threshold": "13:00"
        }

    @staticmethod
    def update_settings(settings):
        settings["_id"] = SettingsModel.SETTINGS_ID
        settings_collection.update_one(
            {"_id": SettingsModel.SETTINGS_ID},
            {"$set": settings},
            upsert=True
        )