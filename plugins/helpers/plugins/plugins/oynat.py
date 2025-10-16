from collections import deque
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls.types import AudioPiped

from main import app, pytgcalls
from helpers.youtube import get_yt_info

# Her sohbet için ayrı bir sıra (kuyruk) tutan sözlük
queues = {}

def get_queue(chat_id):
    """Belirtilen sohbetin sırasını alır veya oluşturur."""
    if chat_id not in queues:
        queues[chat_id] = deque()
    return queues[chat_id]

@Client.on_message(filters.command("play") & ~filters.private)
async def play_music(client, message: Message):
    chat_id = message.chat.id
    query = " ".join(message.command[1:])

    if not query:
        return await message.reply_text("Lütfen bir şarkı adı veya YouTube linki belirtin.\n**Örnek:** `.play In The End`")

    waiting_message = await message.reply_text("🔎 **Aranıyor...**")

    song_info = await get_yt_info(query)
    if not song_info:
        return await waiting_message.edit("❌ **Şarkı bulunamadı.** Lütfen farklı bir anahtar kelimeyle deneyin.")

    queue = get_queue(chat_id)
    queue.append(song_info)

    try:
        call = await pytgcalls.get_call(chat_id)
    except Exception:
        # Daha önce sohbete katılınmamışsa hata verir, bu normaldir.
        call = None

    if not call or not call.is_active:
        try:
            await pytgcalls.join_group_call(
                chat_id,
                AudioPiped(song_info['stream_url']),
            )
            await waiting_message.edit(f"▶️ **Şimdi Çalıyor:**\n[{song_info['title']}]({song_info['url']})\n**Süre:** {song_info['duration']}")
        except Exception as e:
            await waiting_message.edit(f"**Hata:** Sesli sohbete katılamadım. Lütfen botun yetkilerini kontrol edin.\n`{e}`")
    else:
        position = len(queue) - 1
        await waiting_message.edit(f"➕ **Sıraya Eklendi (#{position}):**\n[{song_info['title']}]({song_info['url']})\n**Süre:** {song_info['duration']}")

@pytgcalls.on_stream_end()
async def on_stream_end_handler(_, update):
    """Bir şarkı bittiğinde otomatik olarak sıradakini çalar."""
    chat_id = update.chat_id
    queue = get_queue(chat_id)

    if not queue:
        return

    # Biten şarkıyı listeden çıkar
    queue.popleft()

    if not queue:
        # Sıra boşaldıysa sohbetten ayrıl
        await pytgcalls.leave_group_call(chat_id)
        return

    # Sıradaki şarkıyı çal
    next_song = queue[0]
    try:
        await pytgcalls.change_stream(
            chat_id,
            AudioPiped(next_song['stream_url'])
        )
        await app.send_message(chat_id, f"▶️ **Sıradaki Şarkı:**\n[{next_song['title']}]({next_song['url']})\n**Süre:** {next_song['duration']}")
    except Exception as e:
        print(f"Hata - Sıradaki şarkıya geçilemedi: {e}")
