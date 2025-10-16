# main.py (TÜM HATALAR GİDERİLDİ - FİNAL VERSİYON)

import os
import asyncio
from typing import Dict, List, Tuple
import logging

# Gerekli kütüphaneleri içe aktarma
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from pytgcalls import PyTgCalls
# --- SON DÜZELTME: AudioPiped doğru yoldan (stream) import edildi ---
from pytgcalls.stream import AudioPiped

from yt_dlp import YoutubeDL

# Yapılandırma dosyasından bilgileri çekme
from config import API_ID, API_HASH, BOT_TOKEN, SESSION_STRING

# Hata ayıklama loglarını etkinleştir
logging.basicConfig(level=logging.INFO)

# --- BOT AYARLARI ---
PREFIX = "."
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True, 'nocheckcertificate': True,
    'geo_bypass': True, 'quiet': True, 'no_warnings': True,
}

# --- İSTEMCİLERİ BAŞLATMA ---
app = Client("MusicBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user_client = Client(session_name=SESSION_STRING, api_id=API_ID, api_hash=API_HASH)
pytgcalls = PyTgCalls(user_client)

# Listeler ve Sözlükler
queues: Dict[int, List[Dict]] = {}
active_chats: List[int] = []
now_playing: Dict[int, str] = {}


# --- YARDIMCI FONKSİYONLAR ---

def get_queue(chat_id: int) -> List[Dict]:
    return queues.get(chat_id, [])

def add_to_queue(chat_id: int, title: str, duration: str, filepath: str, link: str, requested_by: str):
    if chat_id not in queues:
        queues[chat_id] = []
    queues[chat_id].append({
        "title": title, "duration": duration, "filepath": filepath,
        "link": link, "requested_by": requested_by
    })

def search_and_download(query: str) -> Tuple[Dict, str]:
    try:
        with YoutubeDL(YTDL_OPTIONS) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
        duration_sec = info.get('duration', 0)
        duration_str = f"{duration_sec // 60}:{duration_sec % 60:02d}"
        filepath = ydl.prepare_filename(info)
        return {
            "filepath": filepath, "title": info.get('title', 'Bilinmeyen Başlık'),
            "duration": duration_str, "link": f"https://www.youtube.com/watch?v={info['id']}"
        }, None
    except Exception as e:
        return None, f"Arama veya indirme sırasında hata: {e}"

async def play_next_song(chat_id: int):
    if chat_id in now_playing and os.path.exists(now_playing[chat_id]):
        os.remove(now_playing[chat_id])
        del now_playing[chat_id]

    queue = get_queue(chat_id)
    if not queue:
        if chat_id in active_chats:
            active_chats.remove(chat_id)
        await pytgcalls.leave_group_call(chat_id)
        await app.send_message(chat_id, "🎵 Çalma listesi bitti, sesli sohbetten ayrıldım.")
        return

    song = queue.pop(0)
    filepath = song['filepath']
    now_playing[chat_id] = filepath
    
    try:
        await pytgcalls.change_stream(chat_id, AudioPiped(filepath))
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🎥 YouTube'da İzle", url=song['link'])]])
        await app.send_message(
            chat_id,
            f"🎵 **Şimdi Çalıyor:**\n\n**Adı:** `{song['title']}`\n**Süre:** `{song['duration']}`\n**İsteyen:** {song['requested_by']}",
            reply_markup=keyboard
        )
    except Exception as e:
        logging.error(f"Sıradaki şarkı çalınırken hata: {e}")
        if chat_id in active_chats:
            active_chats.remove(chat_id)

# --- KOMUTLAR ---

@app.on_message(filters.command("start", prefixes=PREFIX))
async def start_command(_, message: Message):
    await message.reply_text(f"Merhaba! Ben bir müzik botuyum. Komutlar için `{PREFIX}help` yaz.")

@app.on_message(filters.command("help", prefixes=PREFIX))
async def help_command(_, message: Message):
    await message.reply_text(
        f"**🎶 Komut Listesi 🎶**\n\n"
        f"`{PREFIX}play <şarkı adı>` - Şarkı çalar veya sıraya ekler.\n"
        f"`{PREFIX}skip` - Sıradaki şarkıya geçer.\n"
        f"`{PREFIX}pause` - Müziği duraklatır.\n"
        f"`{PREFIX}resume` - Müziği devam ettirir.\n"
        f"`{PREFIX}stop` - Müziği durdurur ve bot ayrılır.\n"
        f"`{PREFIX}queue` - Çalma listesini gösterir."
    )

@app.on_message(filters.command("play", prefixes=PREFIX) & filters.group)
async def play_command(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(f"❓ Örnek: `{PREFIX}play Tarkan Yolla`")

    query = " ".join(message.command[1:])
    chat_id = message.chat.id
    requester = message.from_user.mention
    msg = await message.reply_text("🔄 **Aranıyor ve indiriliyor...**")
    song_data, error = search_and_download(query)
    if error:
        return await msg.edit_text(f"❌ **Hata:** {error}")
    
    is_active = chat_id in active_chats
    if not is_active:
        try:
            await pytgcalls.join_group_call(chat_id, AudioPiped(song_data['filepath']))
            active_chats.append(chat_id)
            now_playing[chat_id] = song_data['filepath']
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🎥 YouTube'da İzle", url=song_data['link'])]])
            await msg.edit_text(
                f"🎵 **Şimdi Çalıyor:**\n\n**Adı:** `{song_data['title']}`\n**Süre:** `{song_data['duration']}`\n**İsteyen:** {requester}",
                reply_markup=keyboard
            )
        except Exception as e:
            await msg.edit_text(f"❌ **Hata:** Sesli sohbete katılamadım. `{e}`")
    else:
        add_to_queue(chat_id, song_data['title'], song_data['duration'], song_data['filepath'], song_data['link'], requester)
        await msg.edit_text(f"➕ **Sıraya Eklendi:** `{song_data['title']}`\n**Pozisyon:** `{len(get_queue(chat_id))}`")

@app.on_message(filters.command("skip", prefixes=PREFIX) & filters.group)
async def skip_command(_, message: Message):
    if not get_queue(message.chat.id):
        return await message.reply_text("⏭️ Sırada başka şarkı yok.")
    await message.reply_text("⏭️ **Şarkı atlandı!**")
    await play_next_song(message.chat.id)

@app.on_message(filters.command("pause", prefixes=PREFIX) & filters.group)
async def pause_command(_, message: Message):
    await pytgcalls.pause_stream(message.chat.id)
    await message.reply_text(f"⏸️ **Müzik duraklatıldı.** Devam etmek için `{PREFIX}resume`.")

@app.on_message(filters.command("resume", prefixes=PREFIX) & filters.group)
async def resume_command(_, message: Message):
    await pytgcalls.resume_stream(message.chat.id)
    await message.reply_text("▶️ **Müzik devam ediyor.**")

@app.on_message(filters.command("stop", prefixes=PREFIX) & filters.group)
async def stop_command(_, message: Message):
    chat_id = message.chat.id
    if chat_id in queues: queues.pop(chat_id)
    if chat_id in now_playing:
        if os.path.exists(now_playing[chat_id]): os.remove(now_playing[chat_id])
        del now_playing[chat_id]
    if chat_id in active_chats: active_chats.remove(chat_id)
    await pytgcalls.leave_group_call(chat_id)
    await message.reply_text("⏹️ **Müzik durduruldu ve sohbetten ayrıldım.**")
    
@app.on_message(filters.command("queue", prefixes=PREFIX) & filters.group)
async def queue_command(_, message: Message):
    queue = get_queue(message.chat.id)
    if not queue:
        return await message.reply_text("📭 Çalma listesi boş.")
    queue_text = "**🎶 Çalma Listesi:**\n\n"
    for i, song in enumerate(queue, 1):
        queue_text += f"`{i}.` **{song['title']}** - `{song['duration']}`\n"
    await message.reply_text(queue_text)

# --- OLAY DİNLEYİCİSİ ---
@pytgcalls.on_stream_end()
async def on_stream_end_handler(_, update):
    await play_next_song(update.chat_id)

# --- BOTU BAŞLATMA ---
async def main():
    logging.info("Bot başlatılıyor...")
    await app.start()
    logging.info("Bot istemcisi başlatıldı.")
    await user_client.start()
    logging.info("Userbot istemcisi başlatıldı.")
    await pytgcalls.start()
    logging.info("PyTgCalls istemcisi başlatıldı. Bot artık hazır!")
    await asyncio.idle()

if __name__ == "__main__":
    try:
        main_loop = asyncio.get_event_loop()
        main_loop.run_until_complete(main())
    except KeyboardInterrupt:
        logging.info("Bot kapatılıyor.")
