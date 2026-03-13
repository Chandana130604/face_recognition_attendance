import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    MONGO_URI = os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/'
    DATABASE_NAME = os.environ.get('DATABASE_NAME') or 'face_attendance'
    FACE_MATCH_TOLERANCE = float(os.environ.get('FACE_MATCH_TOLERANCE') or 0.5)

MONGO_URI = Config.MONGO_URI
DATABASE_NAME = Config.DATABASE_NAME