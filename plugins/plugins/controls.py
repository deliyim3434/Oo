from pyrogram import Client, filters
from pyrogram.types import Message
from main import pytgcalls
from plugins.play import get_queue, queues

@Client.on_message(filters.command("pause") & ~filters.private)
async def pause_stream(_, message: Message):
    chat_id = message.chat.id
    try:
        await pytgcalls.pause_stream(chat_id)
        await message.reply_text("⏸ Müzik duraklatıldı.")
    except Exception as e:
        await message.reply_text(f"Hata: {e}")

@Client.on_message(filters.command("resume") & ~filters.private)
async def resume_stream(_, message: Message):
    chat_id = message.chat.id
    try:
        await pytgcalls.resume_stream(chat_id)
        await message.reply_text("▶️ Müzik devam ettiriliyor.")
    except Exception as e:
        await message.reply_text(f"Hata: {e}")

@Client.on_message(filters.command("skip") & ~filters.private)
async def skip_stream(_, message: Message):
    chat_id = message.chat.id
    queue = get_queue(chat_id)
    if len(queue) < 2:
        return await message.reply_text("Sırada başka şarkı yok.")
    
    try:
        # on_stream_end() fonksiyonunu tetiklemek için akışı değiştir
        next_song = queue[1] # Sıradaki ikinci şarkı
        await pytgcalls.change_stream(
            chat_id,
            AudioPiped(next_song['url'])
        )
        queue.popleft() # Geçilen şarkıyı çıkar
        await message.reply_text(f"⏭ Şarkı atlandı. Şimdi çalan:\n[{next_song['title']}]({next_song['url']})")
    except Exception as e:
        await message.reply_text(f"Hata: {e}")


@Client.on_message(filters.command("stop") & ~filters.private)
async def stop_stream(_, message: Message):
    chat_id = message.chat.id
    try:
        await pytgcalls.leave_group_call(chat_id)
        # Kuyruğu temizle
        if chat_id in queues:
            queues[chat_id].clear()
        await message.reply_text("⏹ Müzik durduruldu ve sesli sohbetten ayrıldım.")
    except Exception as e:
        await message.reply_text(f"Hata: {e}")

@Client.on_message(filters.command("queue") & ~filters.private)
async def show_queue(_, message: Message):
    chat_id = message.chat.id
    queue = get_queue(chat_id)
    
    if not queue:
        return await message.reply_text("Müzik sırası boş.")
    
    queue_text = "🎶 **Müzik Sırası:**\n\n"
    for i, song in enumerate(queue):
        queue_text += f"**{i+1}.** [{song['title']}]({song['url']}) - `{song['duration']}`\n"
        
    await message.reply_text(queue_text, disable_web_page_preview=True)
