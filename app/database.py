import os
import logging
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import redis
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)

def get_mongo_db():
    """
    Initialize MongoDB connection and return the 'worldcup_db' database object.
    """
    try:
        # Create a MongoClient with a timeout so it doesn't hang indefinitely
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        
        # Ping the server to verify the connection
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB.")
        
        # Return the worldcup_db database
        db = client.worldcup_db
        return db
    except ConnectionFailure as e:
        logger.error(f"MongoDB connection failed: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred while connecting to MongoDB: {e}")
        return None

def get_redis_client():
    """
    Initialize Redis connection and return the Redis client object.
    """
    try:
        # Create a Redis client with decode_responses=True so we get strings back
        client = redis.Redis(
            host=REDIS_HOST,
            port=int(REDIS_PORT),
            decode_responses=True
        )
        
        # Ping the server to verify the connection
        client.ping()
        logger.info("Successfully connected to Redis.")
        
        return client
    except redis.ConnectionError as e:
        logger.error(f"Redis connection failed: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred while connecting to Redis: {e}")
        return None

def save_prediction(user_id, home_team, away_team, prediction_result):
    """
    Insert a prediction document into the 'predictions' collection in MongoDB.
    """
    try:
        db = get_mongo_db()
        if db is not None:
            document = {
                "user_id": user_id,
                "home_team": home_team,
                "away_team": away_team,
                "prediction_result": prediction_result,
                "timestamp": datetime.utcnow()
            }
            db.predictions.insert_one(document)
            logger.info(f"Đã lưu dự đoán của user {user_id} vào database")
    except Exception as e:
        logger.error(f"Lỗi khi lưu dự đoán vào database: {e}")

def get_user_history(user_id, limit=5):
    """
    Retrieve the latest prediction history for a specific user from MongoDB.
    """
    try:
        db = get_mongo_db()
        if db is not None:
            # Sort by timestamp descending (-1)
            cursor = db.predictions.find({"user_id": user_id}).sort("timestamp", -1).limit(limit)
            return list(cursor)
        return []
    except Exception as e:
        logger.error(f"Lỗi khi lấy lịch sử dự đoán: {e}")
        return []

def get_global_stats():
    """
    Use MongoDB Aggregation to find the top 5 teams most predicted to win.
    """
    try:
        db = get_mongo_db()
        if db is not None:
            pipeline = [
                {
                    "$project": {
                        "predicted_winner": {
                            "$switch": {
                                "branches": [
                                    {
                                        "case": {
                                            "$and": [
                                                { "$gt": ["$prediction_result.home_win", "$prediction_result.away_win"] },
                                                { "$gt": ["$prediction_result.home_win", "$prediction_result.draw"] }
                                            ]
                                        },
                                        "then": "$home_team"
                                    },
                                    {
                                        "case": {
                                            "$and": [
                                                { "$gt": ["$prediction_result.away_win", "$prediction_result.home_win"] },
                                                { "$gt": ["$prediction_result.away_win", "$prediction_result.draw"] }
                                            ]
                                        },
                                        "then": "$away_team"
                                    }
                                ],
                                "default": "Hòa"
                            }
                        }
                    }
                },
                {
                    "$match": {
                        "predicted_winner": { "$ne": "Hòa" }
                    }
                },
                {
                    "$group": {
                        "_id": "$predicted_winner",
                        "count": { "$sum": 1 }
                    }
                },
                {
                    "$sort": { "count": -1 }
                },
                {
                    "$limit": 5
                }
            ]
            
            return list(db.predictions.aggregate(pipeline))
        return []
    except Exception as e:
        logger.error(f"Lỗi khi lấy thống kê global: {e}")
        return []
