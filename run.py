#!/usr/bin/env python3
import asyncio
import logging
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot import app

async def main():
    try:
        logging.info("Müzik Botu başlatılıyor...")
        await app.start()
        
        # Bot bilgilerini göster
        me = await app.get_me()
        logging.info(f"Bot @{me.username} olarak giriş yaptı")
        logging.info("Bot başarıyla başlatıldı! CTRL+C ile durdurabilirsiniz.")
        
        # Keep the bot running
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        logging.info("Bot kullanıcı tarafından durduruldu!")
    except Exception as e:
        logging.error(f"Bot başlatma hatası: {e}")
    finally:
        await app.stop()
        logging.info("Bot durduruldu!")

if __name__ == "__main__":
    asyncio.run(main())
