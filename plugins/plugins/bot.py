import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import BadRequest, FloodWait

from config import config
from database import update_user_data, get_user_data, update_bot_stats
from music_player import music_player

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot client
app = Client(
    "music_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    plugins=dict(root="plugins")
)

# Start command
@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    user = message.from_user
    user_data = {
        "user_id": user.id,
        "first_name": user.first_name,
        "username": user.username,
        "language_code": user.language_code,
        "last_seen": message.date
    }
    
    await update_user_data(user.id, user_data)
    await update_bot_stats()

    welcome_text = """
🎵 **Müzik Botuna Hoş Geldiniz!**

Ben, Telegram gruplarınızda müzik çalabilen gelişmiş bir botum. 
Aşağıdaki komutlarla beni kullanabilirsiniz:

**🎶 Müzik Komutları:**
/play - Şarkı çal (YouTube URL veya isim)
/skip - Geçerli şarkıyı atla
/pause - Şarkıyı duraklat
/resume - Şarkıyı devam ettir
/stop - Şarkıyı durdur ve kuyruğu temizle
/queue - Şarkı kuyruğunu göster
/nowplaying - Şu an çalan şarkıyı göster

**📊 Bot Komutları:**
/stats - Bot istatistiklerini göster
/help - Yardım mesajını göster

**💡 Örnek Kullanım:**
`/play alone marshmello`
`/play https://www.youtube.com/watch?v=...`
    """

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📚 Komutlar", callback_data="help"),
            InlineKeyboardButton("📊 İstatistik", callback_data="stats")
        ],
        [
            InlineKeyboardButton("🎵 Kanal", url="https://t.me/music_bot_channel"),
            InlineKeyboardButton("👨‍💻 Geliştirici", url="https://t.me/developer")
        ]
    ])

    await message.reply_text(welcome_text, reply_markup=keyboard)

# Help command
@app.on_message(filters.command("help"))
async def help_command(client, message: Message):
    help_text = """
**📚 Kullanılabilir Komutlar:**

**🎶 Müzik Komutları:**
/play [şarkı adı/URL] - Şarkı çal
/skip - Geçerli şarkıyı atla  
/pause - Şarkıyı duraklat
/resume - Şarkıyı devam ettir
/stop - Şarkıyı durdur ve kuyruğu temizle
/queue - Şarkı kuyruğunu göster
/nowplaying - Şu an çalan şarkıyı göster

**📊 Bot Komutları:**
/stats - Bot istatistiklerini göster
/help - Bu yardım mesajını göster

**💡 Önemli Notlar:**
- Botu gruba ekleyip yönetici yapın
- Sesli sohbet özellikleri için botun mikrofon erişimi olmalı
- Maksimum kuyruk boyutu: 50 şarkı
    """

    await message.reply_text(help_text)

# Callback query handler
@app.on_callback_query()
async def handle_callback(client, callback_query):
    data = callback_query.data
    user_id = callback_query.from_user.id
    
    if data == "help":
        await help_command(client, callback_query.message)
    elif data == "stats":
        await stats_command(client, callback_query.message)
    
    await callback_query.answer()

# Error handler
@app.on_error()
async def error_handler(_, update, error):
    logger.error(f"Update {update} caused error: {error}")

# Bot startup
async def main():
    logger.info("Müzik Botu başlatılıyor...")
    await app.start()
    logger.info("Bot başarıyla başlatıldı!")
    
    # Bot bilgilerini göster
    me = await app.get_me()
    logger.info(f"Bot @{me.username} olarak giriş yaptı")
    
    # Bot'u çalışır durumda tut
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot durduruldu!")
    except Exception as e:
        logger.error(f"Bot hatası: {e}")
