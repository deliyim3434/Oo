import asyncio
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch

def format_duration(seconds):
    """Saniyeyi Dakika:Saniye formatına çevirir."""
    if seconds is None:
        return "Bilinmiyor"
    minutes, seconds = divmod(int(seconds), 60)
    return f"{minutes:02d}:{seconds:02d}"

async def get_yt_info(query):
    """YouTube'dan video arar ve ses bilgilerini alır."""
    try:
        # İlk olarak hızlı bir arama yapıp video ID'sini bulalım
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            return None
        
        video_id = results[0]['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        YDL_OPTIONS = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'quiet': True,
        }
        
        loop = asyncio.get_event_loop()
        
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = await loop.run_in_executor(
                None, lambda: ydl.extract_info(video_url, download=False)
            )

        return {
            'title': info.get('title', 'Başlık Yok'),
            'url': video_url,
            'stream_url': info['url'],
            'duration': format_duration(info.get('duration')),
        }
    except Exception as e:
        print(f"YouTube bilgisi alınırken hata: {e}")
        return None
