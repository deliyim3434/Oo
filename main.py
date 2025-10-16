# main.py

import os
import asyncio
from typing import Dict, List, Tuple

# Gerekli kütüphaneleri içe aktarma
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant

from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from pytgcalls.exceptions import GroupCallNotFound

from yt_dlp import YoutubeDL

# Yapılandırma dosyasından bilgileri çekme
from config import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING

# --- BOT AYARLARI ---
# User'ın tercihine göre komut ön eki '.' olarak ayarlandı.
PREFIX = "."
# YouTube-DL için ayarlar
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'noplaylist': True,
    'nocheckcertificate': True,
    'geo_bypass': True,
    'quiet': True,
    'no_warnings': True,
}

# --- İSTEMCİLERİ BAŞLATMA ---
# Bot istemcisi
app = Client("MusicBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
# Sesli arama için yardımcı hesap (userbot) istemcisi
user_client = Client(session_name=SESSION_STRING, api_id=API_ID, api_hash=API_HASH)
# PyTgCalls istemcisi
pytgcalls = PyTgCalls(user_client)


# Çalma listesi (sıra) ve aktif sesli sohbetleri takip etmek için
queues: Dict[int, List[Dict]] = {}
active_chats: List[int] = []


# --- YARDIMCI FONKSİYONLAR ---

def get_queue(chat_id: int) -> List[Dict]:
    """Belirli bir sohbetin çalma listesini alır."""
    return queues.get(chat_id, [])

def add_to_queue(chat_id: int, title: str, duration: str, url: str, link: str, requested_by: str):
    """Sohbetin çalma listesine yeni şarkı ekler."""
    if chat_id not in queues:
        queues[chat_id] = []
    
    queues[chat_id].append({
        "title": title, "duration": duration, "url": url,
        "link": link, "requested_by": requested_by
    })

def search_youtube(query: str) -> Tuple[Dict, str]:
    """YouTube'da arama yapar ve ilk sonucun bilgilerini döndürür."""
    try:
        with YoutubeDL(YTDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        
        # Süreyi dakika:saniye formatına çevirme
        duration_sec = info.get('duration', 0)
        duration_str = f"{duration_sec // 60}:{duration_sec % 60:02d}"

        return {
            "url": info['formats'][0]['url'],
            "title": info.get('title', 'Bilinmeyen Başlık'),
            "duration": duration_str,
            "link": f"https://www.youtube.com/watch?v={info['id']}"
        }, None
    except Exception as e:
        return None, f"Arama sırasında bir hata oluştu: {e}"

async def play_next_song(chat_id: int):
    """Sıradaki şarkıyı çalar."""
    queue = get_queue(chat_id)
    if not queue:
        # Sırada şarkı kalmadıysa sohbetten ayrıl
        if chat_id in active_chats:
            active_chats.remove(chat_id)
        await pytgcalls.leave_group_call(chat_id)
        await app.send_message(chat_id, "🎵 Çalma listesi bitti, sesli sohbetten ayrıldım.")
        return

    song = queue.pop(0)
    try:
        await pytgcalls.change_stream(chat_id, AudioPiped(song['url']))
        
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🎥 YouTube'da İzle", url=song['link'])]])
        await app.send_message(
            chat_id,
            f"🎵 **Şimdi Çalıyor:**\n\n"
            f"**Adı:** `{song['title']}`\n"
            f"**Süre:** `{song['duration']}`\n"
            f"**İsteyen:** {song['requested_by']}",
            reply_markup=keyboard
        )
    except GroupCallNotFound:
        # Eğer manuel olarak kapatılırsa hata vermesin diye
        if chat_id in active_chats:
            active_chats.remove(chat_id)


# --- KOMUTLAR ---

@app.on_message(filters.command("start", prefixes=PREFIX))
async def start_command(_, message: Message):
    await message.reply_text(
        "Merhaba! Ben bir Telegram Müzik Botuyum.\n\n"
        f"Beni bir gruba ekleyin ve sesli sohbeti başlatın. Sonra `{PREFIX}play <şarkı adı>` komutunu kullanabilirsiniz.\n\n"
        f"Tüm komutları görmek için `{PREFIX}help` yazın."
    )

@app.on_message(filters.command("help", prefixes=PREFIX))
async def help_command(_, message: Message):
    await message.reply_text(
        f"**🎶 Komut Listesi 🎶**\n\n"
        f"`{PREFIX}play <şarkı adı veya link>` - Şarkı çalar veya sıraya ekler.\n"
        f"`{PREFIX}skip` - Sıradaki şarkıya geçer.\n"
        f"`{PREFIX}pause` - Çalan müziği duraklatır.\n"
        f"`{PREFIX}resume` - Duraklatılan müziği devam ettirir.\n"
        f"`{PREFIX}stop` - Müziği durdurur ve bot sohbetten ayrılır.\n"
        f"`{PREFIX}queue` - Çalma listesini gösterir."
    )

@app.on_message(filters.command("play", prefixes=PREFIX) & filters.group)
async def play_command(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(f"❓ Lütfen bir şarkı adı veya YouTube linki belirtin.\n\nÖrnek: `{PREFIX}play Tarkan Yolla`")

    query = " ".join(message.command[1:])
    chat_id = message.chat.id
    requester = message.from_user.mention
    
    msg = await message.reply_text("🔄 **Aranıyor...**")

    song_data, error = search_youtube(query)
    if error:
        return await msg.edit_text(f"❌ **Hata:** {error}")
    
    await msg.edit_text("📥 **İndiriliyor ve işleniyor...**")

    # Bot sesli sohbette mi kontrol et
    is_active = chat_id in active_chats
    
    if not is_active:
        # Sesli sohbete katıl ve ilk şarkıyı çal
        try:
            await pytgcalls.join_group_call(chat_id, AudioPiped(song_data['url']))
            active_chats.append(chat_id)
            
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🎥 YouTube'da İzle", url=song_data['link'])]])
            await msg.edit_text(
                f"🎵 **Şimdi Çalıyor:**\n\n"
                f"**Adı:** `{song_data['title']}`\n"
                f"**Süre:** `{song_data['duration']}`\n"
                f"**İsteyen:** {requester}",
                reply_markup=keyboard
            )
        except Exception as e:
            return await msg.edit_text(f"❌ **Hata:** Sesli sohbete katılamadım. Lütfen sesli sohbetin açık olduğundan emin olun.\n\n`{e}`")
    else:
        # Zaten bir şey çalıyorsa sıraya ekle
        add_to_queue(chat_id, song_data['title'], song_data['duration'], song_data['url'], song_data['link'], requester)
        await msg.edit_text(f"➕ **Sıraya Eklendi:** `{song_data['title']}`\n**Pozisyon:** `{len(get_queue(chat_id))}`")

@app.on_message(filters.command("skip", prefixes=PREFIX) & filters.group)
async def skip_command(_, message: Message):
    chat_id = message.chat.id
    if not get_queue(chat_id):
        return await message.reply_text("⏭️ Sırada başka şarkı yok.")
    
    await message.reply_text("⏭️ **Şarkı atlandı!**")
    await play_next_song(chat_id)

@app.on_message(filters.command("pause", prefixes=PREFIX) & filters.group)
async def pause_command(_, message: Message):
    await pytgcalls.pause_stream(message.chat.id)
    await message.reply_text("⏸️ **Müzik duraklatıldı.** Devam etmek için `.resume`.")

@app.on_message(filters.command("resume", prefixes=PREFIX) & filters.group)
async def resume_command(_, message: Message):
    await pytgcalls.resume_stream(message.chat.id)
    await message.reply_text("▶️ **Müzik devam ediyor.**")

@app.on_message(filters.command("stop", prefixes=PREFIX) & filters.group)
async def stop_command(_, message: Message):
    chat_id = message.chat.id
    if chat_id in queues:
        queues.pop(chat_id)
    if chat_id in active_chats:
        active_chats.remove(chat_id)
    await pytgcalls.leave_group_call(chat_id)
    await message.reply_text("⏹️ **Müzik durduruldu ve sohbetten ayrıldım.**")
    
@app.on_message(filters.command("queue", prefixes=PREFIX) & filters.group)
async def queue_command(_, message: Message):
    chat_id = message.chat.id
    queue = get_queue(chat_id)
    if not queue:
        return await message.reply_text("📭 Çalma listesi boş.")

    queue_text = "**🎶 Çalma Listesi:**\n\n"
    for i, song in enumerate(queue, 1):
        queue_text += f"`{i}.` **{song['title']}** - `{song['duration']}`\n"
    
    await message.reply_text(queue_text)

# --- OLAY DİNLEYİCİSİ ---
@pytgcalls.on_stream_end()
async def on_stream_end_handler(_, update):
    """Bir şarkı bittiğinde sıradakini çalar."""
    chat_id = update.chat_id
    await play_next_song(chat_id)


# --- BOTU BAŞLATMA ---
async def main():
    print("Bot başlatılıyor...")
    await app.start()
    print("Bot istemcisi başlatıldı.")
    await user_client.start()
    print("Userbot istemcisi başlatıldı.")
    await pytgcalls.start()
    print("PyTgCalls istemcisi başlatıldı. Bot artık hazır!")
    await asyncio.idle()

if __name__ == "__main__":
    try:
        main_loop = asyncio.get_event_loop()
        main_loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Bot kapatılıyor.")
