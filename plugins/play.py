import os
from collections import deque
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls.types import AudioPiped
from youtube_search import YoutubeSearch
import yt_dlp

from main import pytgcalls # Ana dosyadan pytgcalls'ı import et

# Her sohbet için ayrı bir kuyruk tutacak sözlük
queues = {}

def get_queue(chat_id):
    if chat_id not in queues:
        queues[chat_id] = deque()
    return queues[chat_id]

# YouTube'dan video bilgilerini ve ses URL'sini alır
def get_yt_info(query):
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            return None
        video = results[0]
        video_url = f"https://www.youtube.com{video['url_suffix']}"
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            audio_url = info['url']

        return {
            'title': video['title'],
            'duration': video['duration'],
            'url': audio_url
        }
    except Exception as e:
        print(f"YouTube bilgisi alınırken hata: {e}")
        return None

@Client.on_message(filters.command("play") & ~filters.private)
async def play_music(client, message: Message):
    chat_id = message.chat.id
    query = " ".join(message.command[1:])

    if not query:
        return await message.reply_text("Lütfen bir şarkı adı veya YouTube linki belirtin.\nÖrnek: `.play In The End`")

    # Kullanıcının sesli sohbette olup olmadığını kontrol et
    voice_chat = await pytgcalls.get_call(chat_id)
    
    song = get_yt_info(query)
    if not song:
        return await message.reply_text("Şarkı bulunamadı veya bilgi alınamadı.")

    queue = get_queue(chat_id)
    queue.append(song)
    
    if not voice_chat or not voice_chat.is_active:
        try:
            await pytgcalls.join_group_call(
                chat_id,
                AudioPiped(song['url']),
            )
            await message.reply_text(f"▶️ **Şimdi çalıyor:**\n[{song['title']}]({song['url']})\n**Süre:** {song['duration']}")
        except Exception as e:
            await message.reply_text(f"Sesli sohbete katılırken bir hata oluştu: {e}")
    else:
        await message.reply_text(f"➕ **Sıraya eklendi:**\n[{song['title']}]({song['url']})\n**Süre:** {song['duration']}")

# Bir şarkı bittiğinde sıradakini çalmak için
@pytgcalls.on_stream_end()
async def on_stream_end(_, update):
    chat_id = update.chat_id
    queue = get_queue(chat_id)
    
    if queue:
        queue.popleft() # Biten şarkıyı kuyruktan çıkar
        if queue:
            next_song = queue[0]
            try:
                await pytgcalls.change_stream(
                    chat_id,
                    AudioPiped(next_song['url'])
                )
                await app.send_message(chat_id, f"▶️ **Sıradaki çalıyor:**\n[{next_song['title']}]({next_song['url']})\n**Süre:** {next_song['duration']}")
            except Exception as e:
                print(f"Sıradaki şarkıya geçilirken hata: {e}")
