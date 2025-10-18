unzip telegram-music-bot.zip
cd telegram-music-bot
cp .env.example .env
nano .env  # bilgileri doldur
python3 gen_session.py
python3 bot.py

