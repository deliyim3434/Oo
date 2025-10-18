import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram API credentials
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    
    # Database
    MONGO_URL = os.getenv("MONGO_URL", "")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "music_bot")
    
    # Session
    SESSION_STRING = os.getenv("SESSION_STRING", "")
    
    # Bot settings
    MAX_PLAYLIST_SIZE = 50
    SONG_DOWNLOAD_DIR = "downloads"
    MAX_DURATION = 3600  # 1 hour in seconds
    
    # Ensure downloads directory exists
    if not os.path.exists(SONG_DOWNLOAD_DIR):
        os.makedirs(SONG_DOWNLOAD_DIR)

config = Config()
