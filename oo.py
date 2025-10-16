import os
import asyncio
from dotenv import load_dotenv
from pyrogram import Client
from pytgcalls import PyTgCalls

# .env dosyasındaki değişkenleri yükle
load_dotenv()

# .env dosyasından bilgileri al
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SESSION_NAME = os.getenv("SESSION_NAME")

# Bot istemcisini (client) oluştur
app = Client(
    name=SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins={"root": "plugins"} # Komutların olduğu klasörü belirt
)

# PyTgCalls istemcisini oluştur
pytgcalls = PyTgCalls(app)

# Botu ve PyTgCalls'ı birlikte başlatmak için bir fonksiyon
async def main():
    print("Bot başlatılıyor...")
    await app.start()
    print("PyTgCalls başlatılıyor...")
    await pytgcalls.start()
    print("Bot başarıyla başlatıldı ve çalışıyor!")
    await asyncio.Event().wait() # Botun sürekli çalışmasını sağlar

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
