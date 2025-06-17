from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

load_dotenv()

class MigrationDatabase:
    def __init__(self):
        self.client = MongoClient(
            os.getenv("MONGO_URI"),
            server_api=ServerApi('1')
        )
        self.db = self.client[os.getenv("DB_NAME")]
        self.migration_data = self.db["coll"]
    
    def get_migration_stats(self, filters=None):
        """Get aggregated migration statistics"""
        query = filters or {}
        
        # Get refugees by year
        by_year = list(self.migration_data.aggregate([
            {"$match": query},
            {"$group": {
                "_id": "$Year",
                "total_refugees": {"$sum": {"$toInt": "$Refugees"}},
                "total_asylum": {"$sum": {"$toInt": "$Asylum Seekers"}}
            }},
            {"$sort": {"_id": 1}}
        ]))
        
        # Get top countries
        top_origins = list(self.migration_data.aggregate([
            {"$match": query},
            {"$group": {
                "_id": "$Country of Origin",
                "total_refugees": {"$sum": {"$toInt": "$Refugees"}},
                "iso_code": {"$first": "$Country of Origin ISO"}
            }},
            {"$sort": {"total_refugees": -1}},
            {"$limit": 5}
        ]))
        
        return {
            "by_year": by_year,
            "top_origins": top_origins
        }
    
    def get_raw_data(self, filters=None):
        """Get raw migration data"""
        query = filters or {}
        return list(self.migration_data.find(query, {"_id": 0}))

db = MigrationDatabase()