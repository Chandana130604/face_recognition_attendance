from pymongo import MongoClient

# Use local MongoDB (change if using Atlas)
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "face_attendance"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Collections
employees_collection = db["employees"]
attendance_collection = db["attendance"]
settings_collection = db["settings"]
alerts_collection = db["alerts"]