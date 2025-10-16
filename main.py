import os
import asyncio
from dotenv import load_dotenv
from pyrogram import Client
from pytgcalls import PyTgCalls

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SESSION_NAME = os.getenv("SESSION_NAME")

app = Client(
    name=SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins={"root": "plugins"}
)

pytgcalls = PyTgCalls(app)

async def main():
    print("Bot başlatılıyor...")
    try:
        await app.start()
        print("Pyrogram istemcisi başlatıldı.")
        await pytgcalls.start()
        print("PyTgCalls istemcisi başlatıldı.")
        print("\nBot aktif ve komutları bekliyor!")
        await asyncio.Event().wait()
    except Exception as e:
        print(f"Bot başlatılırken kritik bir hata oluştu: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot kapatılıyor.")
