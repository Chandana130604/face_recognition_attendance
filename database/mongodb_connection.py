from pymongo import MongoClient
from config import MONGO_URI, DATABASE_NAME

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = MongoClient(MONGO_URI)
            cls._instance.db = cls._instance.client[DATABASE_NAME]
        return cls._instance

    def get_collection(self, name):
        return self.db[name]