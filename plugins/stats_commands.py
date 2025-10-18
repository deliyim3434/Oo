import logging
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message

from database import users_collection, music_queues_collection, play_history_collection, bot_stats_collection

logger = logging.getLogger(__name__)

# Stats command
@app.on_message(filters.command("stats"))
async def stats_command(client: Client, message: Message):
    try:
        # Veritabanı istatistikleri
        total_users = await users_collection.count_documents({})
        total_queues = await music_queues_collection.count_documents({})
        total_plays = await play_history_collection.count_documents({})
        
        # Bot istatistikleri
        bot_stats = await bot_stats_collection.find_one({"name": "overall"})
        songs_played = bot_stats.get("songs_played", 0) if bot_stats else 0
        commands_used = bot_stats.get("commands_used", 0) if bot_stats else 0
        
        # Aktif kuyruklar
        active_queues = 0
        async for queue in music_queues_collection.find({}):
            if queue.get("queue"):
                active_queues += 1

        stats_text = (
            "📊 **Bot İstatistikleri**\n\n"
            f"**👥 Toplam Kullanıcı:** {total_users}\n"
            f"**🎵 Toplam Çalınan Şarkı:** {total_plays}\n"
            f"**📈 Aktif Kuyruklar:** {active_queues}\n"
            f"**🔄 Toplam Komut:** {commands_used}\n"
            f"**⚡ Bot Çalışma Süresi:** 24/7\n\n"
            f"**📅 Son Güncelleme:** {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )

        await message.reply_text(stats_text)

    except Exception as e:
        logger.error(f"Stats komutu hatası: {e}")
        await message.reply_text("❌ İstatistikler yüklenirken hata oluştu!")
