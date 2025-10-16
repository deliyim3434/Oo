import os
import asyncio
from collections import deque

from pyrogram import Client, filters
from pyrogram.types import Message
from py_tgcalls import PyTgCalls, StreamType
from py_tgcalls.types.input_stream import InputAudioStream, InputStream

import yt_dlp

# Yapılandırma dosyasından bilgileri içe aktar
from config import API_ID, API_HASH, BOT_TOKEN, SESSION_NAME

# Pyrogram İstemcisi (Bot)
app = Client(
    SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Py-TgCalls İstemcisi
pytgcalls = PyTgCalls(app)

# Şarkı sırasını tutmak için bir liste (deque daha performanslıdır)
playlist = deque()
is_playing = False

# yt-dlp ayarları (sadece ses linkini almak için)
ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
}


# Yardımcı fonksiyon: YouTube'dan ses dosyasını indirir ve yolunu döndürür
def download_song(url_or_query):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Direkt link değilse arama yap
            if "://" not in url_or_query:
                info = ydl.extract_info(f"ytsearch:{url_or_query}", download=False)['entries'][0]
            else:
                info = ydl.extract_info(url_or_query, download=False)

            # En iyi ses formatını seç
            audio_format = None
            for f in info['formats']:
                if f['acodec'] != 'none' and f['vcodec'] == 'none':
                    audio_format = f
                    break
            
            if audio_format is None: # Sadece ses dosyası bulunamazsa en iyisini al
                audio_format = info['formats'][-1]

            return info['title'], audio_format['url']

        except Exception as e:
            print(f"Şarkı indirilirken hata: {e}")
            return None, None

# Bir sonraki şarkıyı çalmak için fonksiyon
async def play_next_song(chat_id):
    global is_playing
    if not playlist:
        is_playing = False
        await pytgcalls.leave_group_call(chat_id)
        return

    # Sıradaki şarkıyı al
    query = playlist.popleft()
    title, stream_url = download_song(query)

    if not stream_url:
        await app.send_message(chat_id, f"❌ `{query}` şarkısı bulunamadı veya indirilemedi. Sıradaki çalınıyor.")
        await play_next_song(chat_id) # Bir sonrakine geç
        return

    # Sesli sohbete katıl
    try:
        await pytgcalls.join_group_call(
            chat_id=chat_id,
            stream=InputAudioStream(stream_url),
            stream_type=StreamType().pulse_stream,
        )
        is_playing = True
        await app.send_message(chat_id, f"🎶 **Şimdi çalıyor:**\n`{title}`")
    except Exception as e:
        await app.send_message(chat_id, f"Sesli sohbete katılırken hata oluştu: {e}")
        is_playing = False

# .play komutu
@app.on_message(filters.command("play", prefixes="."))
async def play_command(_, message: Message):
    global is_playing
    if len(message.command) < 2:
        await message.reply_text("❓ **Kullanım:** `.play <şarkı adı veya YouTube linki>`")
        return

    query = message.text.split(None, 1)[1]
    chat_id = message.chat.id
    
    playlist.append(query)
    await message.reply_text(f"✅ **Sıraya eklendi:** `{query}`")

    if not is_playing:
        await play_next_song(chat_id)

# .skip komutu
@app.on_message(filters.command("skip", prefixes="."))
async def skip_command(_, message: Message):
    chat_id = message.chat.id
    if not is_playing:
        await message.reply_text("❌ Zaten çalan bir şarkı yok.")
        return

    await message.reply_text("⏭️ Şarkı atlanıyor...")
    # Akışı değiştirmek bir sonrakini tetikleyecektir
    await pytgcalls.change_stream(chat_id, InputStream())
    # 'on_end' callback'i olmadığı için bir sonrakini manuel tetikliyoruz
    await play_next_song(chat_id)


# .stop komutu
@app.on_message(filters.command("stop", prefixes="."))
async def stop_command(_, message: Message):
    global is_playing, playlist
    chat_id = message.chat.id
    
    if not is_playing:
        await message.reply_text("❌ Zaten çalan bir şarkı yok.")
        return

    playlist.clear()
    is_playing = False
    await pytgcalls.leave_group_call(chat_id)
    await message.reply_text("⏹️ Müzik durduruldu ve çalma listesi temizlendi.")


# Bot başlatıldığında ve durduğunda PyTgCalls'ı da yönet
async def main():
    print("Bot başlatılıyor...")
    await app.start()
    print("Pyrogram Client başlatıldı.")
    await pytgcalls.start()
    print("PyTgCalls başlatıldı. Bot hazır.")
    await asyncio.Event().wait() # Botun sürekli çalışmasını sağlar
    print("Bot durduruluyor...")
    await app.stop()
    await pytgcalls.stop()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
