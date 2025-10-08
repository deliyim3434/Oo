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

# Telegram API bilgileri (kendi bilgilerinizi girin)
API_ID = 12345678  # 🔁 Buraya kendi API ID'nizi girin
API_HASH = "abcdef1234567890abcdef1234567890"  # 🔁 Buraya kendi API Hash'inizi girin
STRING_SESSION = "AQFDZnYAvFgGqZP8YHh-_fwva4-_QCyXnmFAXIbTVdzdSvZSEe2Vpuq4NrWW-81u5byyPXZx8Hqqk8bus7ZyqkjZ1oi-4KBEDOLBqhTNerf46sOA7PHxZbQ4gd08x3xqlsgmZkHhUzdwjiC8CnO9qGzrsuZ4l33W3_0hQ3UjJDzFZQqhD_JtdVNYMbujVBEjET3w5OfvdtGbqfxdtXPhfVcuY6jBW6bXeSb82jSOLag5688NDsR7cNsnMDAQPlbyuX09-vGMCEr5yPLk-zW4jRQpVat2_LztrLLmefha-1AzLfY16_YNspKoWZXAQuK_ep2LsQEF-GPuIrArwkwVNdaSf8jPgAAAAAH4bcBiAA"  # 🔁 Buraya kendi string session'ınızı girin

# Kullanıcı hesabı oturumu başlatılıyor
app = Client(
    name="banall",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION,
)

# Komut sadece tam olarak ".oo" yazıldığında çalışsın
@app.on_message(filters.command("oo", prefixes=".") & filters.group)
async def banall_command(client, message: Message):
    # kesin kontrol: mesaj tam olarak ".oo" olmalı (ek parametre yok)
    if not message.text or message.text.strip() != ".oo":
        return  # başka bir şey yazıldıysa hiçbir şey yapma

    print(f"{message.chat.id} grubundan üyeler alınıyor...")
    toplam_banlanan = 0
    toplam_hata = 0

    async for uye in client.get_chat_members(message.chat.id):
        try:
            # 1) Kendi hesabını atla
            if uye.user.is_self:
                print("👤 Kendim, atlanıyor.")
                continue

            # 2) Botları atla
            if uye.user.is_bot:
                print(f"🤖 {uye.user.id} bir bot, atlanıyor.")
                continue

            # 3) Yönetici/kurucuyu atla
            if getattr(uye, "status", None) in ("administrator", "creator"):
                print(f"👑 {uye.user.id} yönetici/kurucu, atlanıyor.")
                continue

            # Kullanıcıyı banla
            await client.ban_chat_member(chat_id=message.chat.id, user_id=uye.user.id)
            print(f"✅ {uye.user.id} kullanıcısı banlandı.")
            toplam_banlanan += 1
            await asyncio.sleep(0.5)  # Ban işlemleri arası bekleme süresi (güvenlik)

        except FloodWait as fw:
            print(f"⏸️ FloodWait: {fw.value} saniye bekleniyor...")
            await asyncio.sleep(fw.value)
        except Exception as e:
            print(f"❌ {getattr(uye.user, 'id', 'unknown')} banlanamadı: {e}")
            toplam_hata += 1

    sonuc_mesaji = (
        f"✅ Ban işlemi tamamlandı.\n"
        f"🔨 Toplam Banlanan: {toplam_banlanan}\n"
        f"⚠️ Banlanamayanlar: {toplam_hata}"
    )

    await message.reply(sonuc_mesaji)
    print("✅ İşlem tamamlandı.")

# Başlat
app.start()
print("✅ String Session ile Banall başlatıldı. Komut: .oo (sadece tam yazım çalışır)")
idle()
