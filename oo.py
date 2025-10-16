import os
import asyncio
from dotenv import load_dotenv
from pyrogram import Client
from pytgcalls import PyTgCalls

# .env dosyasındaki değişkenleri sisteme yükler
load_dotenv()

# Konfigürasyon değişkenlerini .env dosyasından okur
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
SESSION_NAME = os.getenv("SESSION_NAME")

# Pyrogram İstemcisi
app = Client(
    name=SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins={"root": "plugins"}  # Komutların olduğu klasörü belirtir
)

# PyTgCalls İstemcisi
pytgcalls = PyTgCalls(app)

async def main():
    """Botu ve PyTgCalls'ı başlatan ana fonksiyon."""
    print("Bot başlatılıyor...")
    try:
        await app.start()
        print("Pyrogram istemcisi başarıyla başlatıldı.")
        await pytgcalls.start()
        print("PyTgCalls istemcisi başarıyla başlatıldı.")
        print("\nBot artık aktif ve komutları dinliyor!")
        await asyncio.Event().wait()  # Botun sürekli çalışmasını sağlar
    except Exception as e:
        print(f"Bot başlatılırken bir hata oluştu: {e}")

if __name__ == "__main__":
    try:
        # Asenkron fonksiyonu çalıştırır
        asyncio.run(main())
    except KeyboardInterrupt:
        # Ctrl+C ile kapatıldığında mesaj verir
        print("\nBot kapatılıyor.")
