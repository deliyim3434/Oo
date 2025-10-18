import logging
from pyrogram import Client, filters
from pyrogram.types import Message

from config import config
from database import update_user_data, update_bot_stats
from music_player import music_player

logger = logging.getLogger(__name__)

# Play command
@app.on_message(filters.command("play"))
async def play_command(client: Client, message: Message):
    try:
        if len(message.command) < 2:
            await message.reply_text("❌ Lütfen bir şarkı adı veya YouTube URL'si girin!\n\nÖrnek: `/play alone marshmello`")
            return

        # Kullanıcı verisini güncelle
        user = message.from_user
        await update_user_data(user.id, {
            "user_id": user.id,
            "first_name": user.first_name,
            "username": user.username,
            "last_command": "play"
        })
        await update_bot_stats()

        query = " ".join(message.command[1:])
        chat_id = message.chat.id

        # Arama mesajı gönder
        search_msg = await message.reply_text("🔍 **Şarkı aranıyor...**")

        # YouTube'da ara
        if "youtube.com" in query or "youtu.be" in query:
            track_data = await music_player.get_direct_url(query)
        else:
            track_data = await music_player.search_youtube(query)

        if not track_data:
            await search_msg.edit_text("❌ Şarkı bulunamadı! Lütfen farklı bir anahtar kelime deneyin.")
            return

        # Kuyruğa ekle
        requested_by = {
            "id": user.id,
            "first_name": user.first_name,
            "username": user.username
        }
        
        track = await music_player.add_to_queue(chat_id, track_data, requested_by)
        
        await search_msg.edit_text(
            f"✅ **Kuyruğa Eklendi!**\n\n"
            f"🎵 **Şarkı:** {track['title']}\n"
            f"⏱ **Süre:** {track['duration']}\n"
            f"👤 **İsteyen:** {user.first_name}\n"
            f"📊 **Sıra Pozisyonu:** {len(music_player.queues[chat_id])}"
        )

        # Eğer çalan müzik yoksa, çalmaya başla
        if not music_player.is_playing[chat_id]:
            await music_player.play_music(client, chat_id, message)

    except Exception as e:
        logger.error(f"Play komutu hatası: {e}")
        await message.reply_text("❌ Bir hata oluştu! Lütfen daha sonra tekrar deneyin.")

# Skip command
@app.on_message(filters.command("skip"))
async def skip_command(client: Client, message: Message):
    try:
        chat_id = message.chat.id
        queue_info = music_player.get_queue_info(chat_id)
        
        if not queue_info["current"] and not queue_info["queue"]:
            await message.reply_text("❌ Çalan şarkı veya kuyruk yok!")
            return

        if await music_player.skip_music(chat_id):
            await message.reply_text("⏭ **Şarkı atlandı!**")
            
            # Sıradaki şarkıyı çal
            if music_player.queues[chat_id]:
                await music_player.play_music(client, chat_id, message)
        else:
            await message.reply_text("❌ Şarkı atlanamadı!")

    except Exception as e:
        logger.error(f"Skip komutu hatası: {e}")
        await message.reply_text("❌ Bir hata oluştu!")

# Queue command
@app.on_message(filters.command("queue"))
async def queue_command(client: Client, message: Message):
    try:
        chat_id = message.chat.id
        queue_info = music_player.get_queue_info(chat_id)
        
        if not queue_info["current"] and not queue_info["queue"]:
            await message.reply_text("📭 **Kuyruk boş!**\n\nBir şarkı çalmak için `/play` komutunu kullanın.")
            return

        queue_text = "📋 **Müzik Kuyruğu**\n\n"
        
        # Şu an çalan şarkı
        if queue_info["current"]:
            current = queue_info["current"]
            status = "⏸ Duraklatıldı" if queue_info["is_paused"] else "▶️ Çalıyor"
            queue_text += f"**🎵 Şu An Çalıyor ({status}):**\n"
            queue_text += f"**{current['title']}**\n"
            queue_text += f"⏱ {current['duration']} | 👤 {current['requested_by']['first_name']}\n\n"

        # Kuyruktaki şarkılar
        queue = queue_info["queue"]
        if queue:
            queue_text += f"**📊 Sıradaki Şarkılar ({len(queue)}):**\n"
            for i, track in enumerate(queue[:10], 1):
                queue_text += f"**{i}. {track['title']}**\n"
                queue_text += f"   ⏱ {track['duration']} | 👤 {track['requested_by']['first_name']}\n"

            if len(queue) > 10:
                queue_text += f"\n... ve {len(queue) - 10} şarkı daha"

        await message.reply_text(queue_text)

    except Exception as e:
        logger.error(f"Queue komutu hatası: {e}")
        await message.reply_text("❌ Kuyruk gösterilirken hata oluştu!")

# Now Playing command
@app.on_message(filters.command(["nowplaying", "np"]))
async def now_playing_command(client: Client, message: Message):
    try:
        chat_id = message.chat.id
        queue_info = music_player.get_queue_info(chat_id)
        
        if not queue_info["current"]:
            await message.reply_text("❌ Şu an çalan şarkı yok!")
            return

        current = queue_info["current"]
        status = "⏸ Duraklatıldı" if queue_info["is_paused"] else "▶️ Çalıyor"
        
        now_playing_text = (
            f"🎵 **Şu An Çalıyor ({status})**\n\n"
            f"**📀 Şarkı:** {current['title']}\n"
            f"**⏱ Süre:** {current['duration']}\n"
            f"**👤 İsteyen:** {current['requested_by']['first_name']}\n"
            f"**📊 Kuyruk:** {len(queue_info['queue'])} şarkı\n\n"
        )

        # Kontrol butonları
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⏸ Duraklat", callback_data="pause"),
                InlineKeyboardButton("▶️ Devam", callback_data="resume"),
                InlineKeyboardButton("⏭ Atla", callback_data="skip")
            ]
        ])

        await message.reply_text(now_playing_text, reply_markup=keyboard)

    except Exception as e:
        logger.error(f"NowPlaying komutu hatası: {e}")
        await message.reply_text("❌ Bir hata oluştu!")

# Pause command
@app.on_message(filters.command("pause"))
async def pause_command(client: Client, message: Message):
    try:
        chat_id = message.chat.id
        
        if await music_player.pause_music(chat_id):
            await message.reply_text("⏸ **Müzik duraklatıldı!**")
        else:
            await message.reply_text("❌ Çalan müzik yok veya zaten duraklatılmış!")

    except Exception as e:
        logger.error(f"Pause komutu hatası: {e}")
        await message.reply_text("❌ Bir hata oluştu!")

# Resume command
@app.on_message(filters.command("resume"))
async def resume_command(client: Client, message: Message):
    try:
        chat_id = message.chat.id
        
        if await music_player.resume_music(chat_id):
            await message.reply_text("▶️ **Müzik devam ediyor!**")
        else:
            await message.reply_text("❌ Duraklatılmış müzik yok!")

    except Exception as e:
        logger.error(f"Resume komutu hatası: {e}")
        await message.reply_text("❌ Bir hata oluştu!")

# Stop command
@app.on_message(filters.command("stop"))
async def stop_command(client: Client, message: Message):
    try:
        chat_id = message.chat.id
        await music_player.stop_music(chat_id)
        await message.reply_text("⏹ **Müzik durduruldu ve kuyruk temizlendi!**")

    except Exception as e:
        logger.error(f"Stop komutu hatası: {e}")
        await message.reply_text("❌ Bir hata oluştu!")
