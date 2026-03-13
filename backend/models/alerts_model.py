from database.db_connection import alerts_collection
from datetime import datetime

class AlertModel:
    @staticmethod
    def create_alert(message):
        doc = {
            "message": message,
            "timestamp": datetime.now()
        }
        alerts_collection.insert_one(doc)

    @staticmethod
    def get_recent(limit=5):
        return list(alerts_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(limit))