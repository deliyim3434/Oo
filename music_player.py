import os
import asyncio
import logging
from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime

import yt_dlp
from pyrogram import Client
from pyrogram.types import Message

from config import config
from database import update_queue, get_queue, add_play_history, update_bot_stats

logger = logging.getLogger(__name__)

class MusicPlayer:
    def __init__(self):
        self.queues: Dict[int, List] = defaultdict(list)
        self.current_playing: Dict[int, Dict] = {}
        self.is_playing: Dict[int, bool] = defaultdict(bool)
        self.is_paused: Dict[int, bool] = defaultdict(bool)
        
        # YouTube DL options
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(config.SONG_DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch',
            'source_address': '0.0.0.0',
            'extractaudio': True,
            'audioformat': 'mp3',
            'noprogress': True,
        }

    async def search_youtube(self, query: str) -> Optional[Dict]:
        """YouTube'da müzik ara"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{query}", download=False)
                if info and 'entries' in info and info['entries']:
                    return info['entries'][0]
        except Exception as e:
            logger.error(f"YouTube arama hatası: {e}")
        return None

    async def get_direct_url(self, url: str) -> Optional[Dict]:
        """Direct streaming URL'si al"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info
        except Exception as e:
            logger.error(f"URL çözümleme hatası: {e}")
        return None

    async def add_to_queue(self, chat_id: int, track_data: Dict, requested_by: Dict) -> Dict:
        """Kuyruğa müzik ekle"""
        track = {
            "title": track_data.get('title', 'Bilinmeyen'),
            "url": track_data.get('url') or track_data.get('webpage_url'),
            "duration": self.format_duration(track_data.get('duration', 0)),
            "requested_by": requested_by,
            "thumbnail": track_data.get('thumbnail'),
            "added_at": datetime.now()
        }
        
        self.queues[chat_id].append(track)
        await update_queue(chat_id, self.queues[chat_id])
        
        return track

    async def play_music(self, client: Client, chat_id: int, message: Message):
        """Müzik çalmaya başla"""
        if self.is_playing[chat_id] or not self.queues[chat_id]:
            return

        self.is_playing[chat_id] = True
        self.is_paused[chat_id] = False

        while self.queues[chat_id] and self.is_playing[chat_id]:
            if self.is_paused[chat_id]:
                await asyncio.sleep(1)
                continue

            track = self.queues[chat_id].pop(0)
            self.current_playing[chat_id] = track
            await update_queue(chat_id, self.queues[chat_id])

            try:
                # Müzik çalma bilgisini göster
                await message.reply_text(
                    f"🎵 **Şimdi Çalıyor:** {track['title']}\n"
                    f"⏱ **Süre:** {track['duration']}\n"
                    f"👤 **İsteyen:** {track['requested_by']['first_name']}\n"
                    f"📊 **Kuyruk:** {len(self.queues[chat_id])} şarkı"
                )

                # Oynatma geçmişine ekle
                await add_play_history(chat_id, track)
                await update_bot_stats()

                # Simüle edilmiş çalma süresi (gerçek uygulamada ses akışı olacak)
                duration = 180  # 3 dakika simülasyon
                await asyncio.sleep(duration)

            except Exception as e:
                logger.error(f"Çalma hatası: {e}")
                await message.reply_text("❌ Müzik çalınırken hata oluştu!")

        self.is_playing[chat_id] = False
        self.current_playing[chat_id] = None

    async def skip_music(self, chat_id: int) -> bool:
        """Müziği atla"""
        if self.is_playing[chat_id]:
            self.is_playing[chat_id] = False
            await asyncio.sleep(1)
            return True
        return False

    async def pause_music(self, chat_id: int) -> bool:
        """Müziği duraklat"""
        if self.is_playing[chat_id] and not self.is_paused[chat_id]:
            self.is_paused[chat_id] = True
            return True
        return False

    async def resume_music(self, chat_id: int) -> bool:
        """Müziği devam ettir"""
        if self.is_playing[chat_id] and self.is_paused[chat_id]:
            self.is_paused[chat_id] = False
            return True
        return False

    async def stop_music(self, chat_id: int):
        """Müziği durdur ve kuyruğu temizle"""
        self.is_playing[chat_id] = False
        self.is_paused[chat_id] = False
        self.queues[chat_id].clear()
        self.current_playing[chat_id] = None
        await update_queue(chat_id, [])

    def format_duration(self, duration: int) -> str:
        """Saniyeyi dakika:saniye formatına çevir"""
        if not duration:
            return "Bilinmiyor"
        minutes, seconds = divmod(duration, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def get_queue_info(self, chat_id: int) -> Dict:
        """Kuyruk bilgilerini getir"""
        current = self.current_playing.get(chat_id)
        queue = self.queues.get(chat_id, [])
        
        return {
            "current": current,
            "queue": queue,
            "is_playing": self.is_playing[chat_id],
            "is_paused": self.is_paused[chat_id]
        }

# Global player instance
music_player = MusicPlayer()
