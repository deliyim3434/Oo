import os
import logging
import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pyrogram.errors import FloodWait

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

# Ayarlar - API bilgilerinizi girin
API_ID = 12345678  # Buraya kendi API ID'nizi girin
API_HASH = "abcdef1234567890abcdef1234567890"  # Buraya kendi API Hash'inizi girin
STRING_SESSION = "YOUR_STRING_SESSION_HERE"  # Buraya string session'ınızı girin

# Client oluşturuluyor
app = Client(
    name="banall",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION,
)

@app.on_message(filters.command("falo", prefixes=".") & filters.group)
async def banall_command(client, message: Message):
    print(f"{message.chat.id} grubundan üyeler alınıyor...")
    toplam_banlanan = 0
    toplam_hata = 0

    async for uye in client.get_chat_members(message.chat.id):
        try:
            await client.ban_chat_member(chat_id=message.chat.id, user_id=uye.user.id)
            print(f"{uye.user.id} kullanıcısı banlandı.")
            toplam_banlanan += 1
            await asyncio.sleep(0.05)
        except FloodWait as fw:
            print(f"⏸️ FloodWait: {fw.value} saniye bekleniyor...")
            await asyncio.sleep(fw.value)
        except Exception as e:
            print(f"{uye.user.id} banlanamadı: {e}")
            toplam_hata += 1

    sonuc_mesaji = (
        f"✅ Ban işlemi tamamlandı.\n"
        f"🔨 Toplam Banlanan: {toplam_banlanan}\n"
        f"⚠️ Banlanamayanlar: {toplam_hata}"
    )

    await message.reply(sonuc_mesaji)
    print("İşlem tamamlandı.")

# Başlatılıyor
app.start()
print("✅ Kullanıcı oturumu (String Session) ile başlatıldı.")
idle()
