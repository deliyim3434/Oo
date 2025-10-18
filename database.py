import logging
from motor.motor_asyncio import AsyncIOMotorClient
from config import config

logger = logging.getLogger(__name__)

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()

    def connect(self):
        try:
            self.client = AsyncIOMotorClient(config.MONGO_URL)
            self.db = self.client[config.DATABASE_NAME]
            logger.info("MongoDB bağlantısı başarılı!")
        except Exception as e:
            logger.error(f"MongoDB bağlantı hatası: {e}")

    def get_collection(self, name):
        return self.db[name]

# Collections
db = MongoDB()
users_collection = db.get_collection("users")
music_queues_collection = db.get_collection("queues")
play_history_collection = db.get_collection("play_history")
bot_stats_collection = db.get_collection("stats")

async def update_user_data(user_id: int, user_data: dict):
    await users_collection.update_one(
        {"user_id": user_id},
        {"$set": user_data},
        upsert=True
    )

async def get_user_data(user_id: int):
    return await users_collection.find_one({"user_id": user_id})

async def update_queue(chat_id: int, queue: list):
    await music_queues_collection.update_one(
        {"chat_id": chat_id},
        {"$set": {"queue": queue, "updated_at": datetime.now()}},
        upsert=True
    )

async def get_queue(chat_id: int):
    data = await music_queues_collection.find_one({"chat_id": chat_id})
    return data.get("queue", []) if data else []

async def add_play_history(chat_id: int, track_data: dict):
    await play_history_collection.insert_one({
        "chat_id": chat_id,
        **track_data,
        "played_at": datetime.now()
    })

async def update_bot_stats():
    await bot_stats_collection.update_one(
        {"name": "overall"},
        {
            "$inc": {"songs_played": 1, "commands_used": 1},
            "$set": {"last_updated": datetime.now()}
        },
        upsert=True
    )
