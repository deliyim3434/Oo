#!/usr/bin/env python3
import os
import sys
import subprocess

def setup_bot():
    print("🎵 Telegram Müzik Botu Kurulumu")
    print("=" * 40)
    
    # Gerekli paketleri yükle
    print("\n📦 Gerekli paketler yükleniyor...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # .env dosyasını kontrol et
    if not os.path.exists(".env"):
        print("\n🔧 .env dosyası oluşturuluyor...")
        with open(".env", "w") as f:
            f.write("""API_ID=your_api_id_here
API_HASH=your_api_hash_here
BOT_TOKEN=your_bot_token_here
MONGO_URL=your_mongodb_connection_string_here
DATABASE_NAME=music_bot
SESSION_STRING=your_session_string_here
""")
        print("✅ .env dosyası oluşturuldu. Lütfen bilgilerinizi güncelleyin!")
    
    # Downloads klasörünü oluştur
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
        print("✅ Downloads klasörü oluşturuldu!")
    
    print("\n🎉 Kurulum tamamlandı!")
    print("\n📝 Yapılacaklar:")
    print("1. .env dosyasındaki bilgileri doldurun")
    print("2. MongoDB bağlantı URL'sini ayarlayın")
    print("3. Botu çalıştırmak için: python run.py")
    print("\n💡 Yardım için: https://t.me/developer")

if __name__ == "__main__":
    setup_bot()
