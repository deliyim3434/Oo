from pyrogram import Client, filters
from pyrogram.types import Message

from main import pytgcalls
from plugins.oynat import get_queue, queues, on_stream_end_handler
from pytgcalls.types import AudioPiped


@Client.on_message(filters.command("pause") & ~filters.private)
async def pause_stream(_, message: Message):
    chat_id = message.chat.id
    try:
        await pytgcalls.pause_stream(chat_id)
        await message.reply_text("⏸ **Müzik duraklatıldı.**\nDevam etmek için `.resume` komutunu kullanın.")
    except Exception as e:
        await message.reply_text(f"❌ Bir hata oluştu: `{e}`")

@Client.on_message(filters.command("resume") & ~filters.private)
async def resume_stream(_, message: Message):
    chat_id = message.chat.id
    try:
        await pytgcalls.resume_stream(chat_id)
        await message.reply_text("▶️ **Müzik devam ettiriliyor.**")
    except Exception as e:
        await message.reply_text(f"❌ Bir hata oluştu: `{e}`")

@Client.on_message(filters.command("stop") & ~filters.private)
async def stop_stream(_, message: Message):
    chat_id = message.chat.id
    try:
        # Kuyruğu temizle
        if chat_id in queues:
            queues[chat_id].clear()
        
        await pytgcalls.leave_group_call(chat_id)
        await message.reply_text("⏹️ **Müzik durduruldu ve sesli sohbetten ayrıldım.**")
    except Exception as e:
        await message.reply_text(f"❌ Bir hata oluştu: `{e}`")

@Client.on_message(filters.command("skip") & ~filters.private)
async def skip_stream(_, message: Message):
    chat_id = message.chat.id
    queue = get_queue(chat_id)
    if len(queue) < 2:
        return await message.reply_text("Sırada atlanacak başka şarkı yok.")
    
    # Atlanan şarkıyı listeden çıkar
    skipped_song = queue.popleft()
    
    # Sıradaki şarkıyı çal
    next_song = queue[0]
    try:
        await pytgcalls.change_stream(
            chat_id,
            AudioPiped(next_song['stream_url'])
        )
        await message.reply_text(f"⏭️ **Şarkı Atlandı!**\n\n**Şimdi Çalıyor:**\n[{next_song['title']}]({next_song['url']})")
    except Exception as e:
        await message.reply_text(f"❌ Bir hata oluştu: `{e}`")


@Client.on_message(filters.command("queue") & ~filters.private)
async def show_queue(_, message: Message):
    chat_id = message.chat.id
    queue = get_queue(chat_id)
    
    if not queue:
        return await message.reply_text("🎶 **Sıra boş.** Müzik eklemek için `.play` komutunu kullanın.")
    
    queue_text = "🎶 **Müzik Sırası:**\n\n"
    for i, song in enumerate(list(queue)):
        if i == 0:
            queue_text += f"▶️ **Şimdi Çalıyor:** [{song['title']}]({song['url']}) - `{song['duration']}`\n\n"
        else:
            queue_text += f"**{i}.** [{song['title']}]({song['url']}) - `{song['duration']}`\n"
            
    await message.reply_text(queue_text, disable_web_page_preview=True)
