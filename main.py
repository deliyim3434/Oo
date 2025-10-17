# -*- coding: utf-8 -*-

"""
TÜM OYUNLARI İÇEREN TELEGRAM BOTU - TEK DOSYA SÜRÜMÜ

Bu dosya, istenen tüm oyunları içeren eksiksiz bir Telegram botudur.
Çalıştırmak için:
1. Gerekli kütüphaneyi yükleyin: pip install python-telegram-bot
2. Aşağıdaki BOT_TOKEN değişkenine kendi bot token'ınızı yapıştırın.
3. Dosyayı `python bot.py` komutuyla çalıştırın.
"""

import logging
import random
import asyncio
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. AYARLAR VE BOT TOKEN ---

# BotFather'dan aldığınız token'ı buraya yapıştırın.
BOT_TOKEN = "7651843103:AAGiChGdicvHQ9LOhV_Pk0hhqaF4fAWaEVw"

# Hata ayıklama için loglamayı etkinleştir
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# --- 2. OYUN MANTIKLARI VE VERİLERİ ---

# Her oyunun aktif durumunu takip etmek için ayrı sözlükler (dictionary)
sayi_oyunu_games = {}
hizli_mat_games = {}
kelime_zinciri_games = {}
plaka_oyunu_games = {}
bayrak_oyunu_games = {}
bilgi_oyunu_games = {}
bul_bakalim_games = {}
pi_oyunu_games = {}
hafiza_simsegi_games = {}
bosluk_doldurma_games = {}


# --- SAYI OYUNU (SICAK-SOĞUK) ---
async def start_sayi_oyunu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if any(chat_id in g for g in [hizli_mat_games, kelime_zinciri_games, plaka_oyunu_games, bayrak_oyunu_games, bilgi_oyunu_games, bul_bakalim_games, pi_oyunu_games, hafiza_simsegi_games, bosluk_doldurma_games]):
        await update.message.reply_text("Lütfen önce devam eden diğer oyunu bitirin.")
        return
    
    target_number = random.randint(1, 100)
    sayi_oyunu_games[chat_id] = {'number': target_number, 'last_diff': None}
    await update.message.reply_text("Sıcak-Soğuk oyununa hoş geldin! 🔥❄️\n1 ile 100 arasında bir sayı tuttum. Tahmin et bakalım!\nOyunu bitirmek için /sayibitir yaz.")

async def guess_sayi_oyunu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        user_guess = int(update.message.text)
        target = sayi_oyunu_games[chat_id]['number']
        if user_guess == target:
            await update.message.reply_text(f"🎉 TEBRİKLER! 🎉 Doğru sayıyı buldun: {target}")
            del sayi_oyunu_games[chat_id]
        else:
            current_diff = abs(target - user_guess)
            last_diff = sayi_oyunu_games[chat_id].get('last_diff')
            if last_diff is None or current_diff < last_diff:
                await update.message.reply_text("🔥 Isınıyorsun...")
            else:
                await update.message.reply_text("❄️ Soğuyorsun...")
            sayi_oyunu_games[chat_id]['last_diff'] = current_diff
    except (ValueError, TypeError):
        await update.message.reply_text("Lütfen sadece sayı girin.")

async def stop_sayi_oyunu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in sayi_oyunu_games:
        correct_number = sayi_oyunu_games[chat_id]['number']
        del sayi_oyunu_games[chat_id]
        await update.message.reply_text(f"Oyun bitirildi. Doğru sayı {correct_number} idi.")
    else:
        await update.message.reply_text("Aktif bir sayı oyunu yok.")


# --- HIZLI MATEMATİK ---
async def start_hizli_matematik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if any(chat_id in g for g in [sayi_oyunu_games, kelime_zinciri_games, plaka_oyunu_games, bayrak_oyunu_games, bilgi_oyunu_games, bul_bakalim_games, pi_oyunu_games, hafiza_simsegi_games, bosluk_doldurma_games]):
        await update.message.reply_text("Lütfen önce devam eden diğer oyunu bitirin.")
        return
        
    num1, num2 = random.randint(1, 20), random.randint(1, 20)
    operator = random.choice(['+', '-', '*'])
    if operator == '+': answer = num1 + num2
    elif operator == '-':
        if num1 < num2: num1, num2 = num2, num1
        answer = num1 - num2
    else: answer = num1 * num2
    question = f"Hızlıca cevapla: {num1} {operator} {num2} = ?"
    hizli_mat_games[chat_id] = {'answer': answer}
    await update.message.reply_text(question)

async def check_answer_hizli_matematik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    try:
        user_answer = int(update.message.text)
        correct_answer = hizli_mat_games[chat_id]['answer']
        if user_answer == correct_answer:
            await update.message.reply_text("✅ Doğru! Tebrikler!")
        else:
            await update.message.reply_text(f"❌ Yanlış! Doğru cevap {correct_answer} idi.")
        del hizli_mat_games[chat_id]
    except (ValueError, TypeError):
        pass # Ignore non-numeric answers

# --- KELİME ZİNCİRİ ---
async def start_kelime_zinciri(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if any(chat_id in g for g in [sayi_oyunu_games, hizli_mat_games, plaka_oyunu_games, bayrak_oyunu_games, bilgi_oyunu_games, bul_bakalim_games, pi_oyunu_games, hafiza_simsegi_games, bosluk_doldurma_games]):
        await update.message.reply_text("Lütfen önce devam eden diğer oyunu bitirin.")
        return

    kelime_zinciri_games[chat_id] = {'last_word': None}
    await update.message.reply_text("Kelime Zinciri başladı! ⛓️\nBir kelime yazarak oyunu başlatın.\nBitirmek için /zinciribitir yazın.")

async def play_kelime_zinciri(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    word = update.message.text.lower().strip()
    if not word.isalpha(): return
    
    game = kelime_zinciri_games[chat_id]
    last_word = game.get('last_word')
    
    if last_word:
        if word.startswith(last_word[-1]):
            game['last_word'] = word
            await update.message.reply_text(f"Güzel! Sıradaki kelime '{word[-1].upper()}' harfi ile başlamalı.")
        else:
            await update.message.reply_text(f"Geçersiz! Kelime '{last_word[-1].upper()}' ile başlamalıydı.")
    else:
        game['last_word'] = word
        await update.message.reply_text(f"Başladık! Sıradaki kelime '{word[-1].upper()}' harfi ile başlamalı.")

async def stop_kelime_zinciri(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in kelime_zinciri_games:
        del kelime_zinciri_games[chat_id]
        await update.message.reply_text("Kelime Zinciri oyunu bitirildi.")
    else:
        await update.message.reply_text("Aktif bir Kelime Zinciri oyunu yok.")

# --- PLAKA OYUNU ---
PLATES = { "01": "Adana", "02": "Adıyaman", "03": "Afyonkarahisar", "04": "Ağrı", "05": "Amasya", "06": "Ankara", "07": "Antalya", "08": "Artvin", "09": "Aydın", "10": "Balıkesir", "11": "Bilecik", "12": "Bingöl", "13": "Bitlis", "14": "Bolu", "15": "Burdur", "16": "Bursa", "17": "Çanakkale", "18": "Çankırı", "19": "Çorum", "20": "Denizli", "21": "Diyarbakır", "22": "Edirne", "23": "Elazığ", "24": "Erzincan", "25": "Erzurum", "26": "Eskişehir", "27": "Gaziantep", "28": "Giresun", "29": "Gümüşhane", "30": "Hakkari", "31": "Hatay", "32": "Isparta", "33": "Mersin", "34": "İstanbul", "35": "İzmir", "36": "Kars", "37": "Kastamonu", "38": "Kayseri", "39": "Kırklareli", "40": "Kırşehir", "41": "Kocaeli", "42": "Konya", "43": "Kütahya", "44": "Malatya", "45": "Manisa", "46": "Kahramanmaraş", "47": "Mardin", "48": "Muğla", "49": "Muş", "50": "Nevşehir", "51": "Niğde", "52": "Ordu", "53": "Rize", "54": "Sakarya", "55": "Samsun", "56": "Siirt", "57": "Sinop", "58": "Sivas", "59": "Tekirdağ", "60": "Tokat", "61": "Trabzon", "62": "Tunceli", "63": "Şanlıurfa", "64": "Uşak", "65": "Van", "66": "Yozgat", "67": "Zonguldak", "68": "Aksaray", "69": "Bayburt", "70": "Karaman", "71": "Kırıkkale", "72": "Batman", "73": "Şırnak", "74": "Bartın", "75": "Ardahan", "76": "Iğdır", "77": "Yalova", "78": "Karabük", "79": "Kilis", "80": "Osmaniye", "81": "Düzce"}

async def start_plaka_oyunu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if any(chat_id in g for g in [sayi_oyunu_games, hizli_mat_games, kelime_zinciri_games, bayrak_oyunu_games, bilgi_oyunu_games, bul_bakalim_games, pi_oyunu_games, hafiza_simsegi_games, bosluk_doldurma_games]):
        await update.message.reply_text("Lütfen önce devam eden diğer oyunu bitirin.")
        return

    mode = random.choice(['plaka_sor', 'sehir_sor'])
    if mode == 'plaka_sor':
        plate, city = random.choice(list(PLATES.items()))
        question = f"'{city}' şehrinin plakası nedir?"
        answer = plate
    else:
        plate, city = random.choice(list(PLATES.items()))
        question = f"'{plate}' plakası hangi şehre aittir?"
        answer = city
    plaka_oyunu_games[chat_id] = {'answer': answer}
    await update.message.reply_text(question)

async def check_answer_plaka_oyunu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_answer = update.message.text.strip()
    correct_answer = plaka_oyunu_games[chat_id]['answer']
    if user_answer.lower() == correct_answer.lower():
        await update.message.reply_text(f"✅ Doğru! Cevap: {correct_answer}")
    else:
        await update.message.reply_text(f"❌ Yanlış! Doğru cevap: {correct_answer}")
    del plaka_oyunu_games[chat_id]

# --- BAYRAK OYUNU ---
FLAGS = { "🇹🇷": ["türkiye", "turkey"], "🇩🇪": ["almanya", "germany"], "🇫🇷": ["fransa", "france"], "🇮🇹": ["italya", "italy"], "🇪🇸": ["ispanya", "spain"], "🇬🇧": ["birleşik krallık", "ingiltere", "united kingdom"], "🇺🇸": ["amerika", "abd", "usa"], "🇨🇳": ["çin", "china"], "🇯🇵": ["japonya", "japan"], "🇷🇺": ["rusya", "russia"] }

async def start_bayrak_oyunu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if any(chat_id in g for g in [sayi_oyunu_games, hizli_mat_games, kelime_zinciri_games, plaka_oyunu_games, bilgi_oyunu_games, bul_bakalim_games, pi_oyunu_games, hafiza_simsegi_games, bosluk_doldurma_games]):
        await update.message.reply_text("Lütfen önce devam eden diğer oyunu bitirin.")
        return

    flag, names = random.choice(list(FLAGS.items()))
    bayrak_oyunu_games[chat_id] = {'answer': names}
    await update.message.reply_text(f"Bu bayrak hangi ülkeye ait? {flag}")

async def check_answer_bayrak_oyunu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_answer = update.message.text.strip().lower()
    correct_answers = bayrak_oyunu_games[chat_id]['answer']
    if user_answer in correct_answers:
        await update.message.reply_text(f"✅ Doğru! Cevap: {correct_answers[0].title()}")
    else:
        await update.message.reply_text(f"❌ Yanlış! Doğru cevap: {correct_answers[0].title()}")
    del bayrak_oyunu_games[chat_id]
    
# --- BİLGİ OYUNU ---
QUESTIONS = { "Türkiye'nin başkenti neresidir?": "Ankara", "Everest Dağı hangi kıtadadır?": "Asya", "Suyun kimyasal formülü nedir?": "H2O", "Dünyanın en büyük okyanusu hangisidir?": "Pasifik", "Fatih Sultan Mehmet, İstanbul'u hangi yılda fethetmiştir?": "1453" }

async def start_bilgi_oyunu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if any(chat_id in g for g in [sayi_oyunu_games, hizli_mat_games, kelime_zinciri_games, plaka_oyunu_games, bayrak_oyunu_games, bul_bakalim_games, pi_oyunu_games, hafiza_simsegi_games, bosluk_doldurma_games]):
        await update.message.reply_text("Lütfen önce devam eden diğer oyunu bitirin.")
        return

    question, answer = random.choice(list(QUESTIONS.items()))
    bilgi_oyunu_games[chat_id] = {'answer': answer}
    await update.message.reply_text(f"Soru geliyor:\n\n{question}")

async def check_answer_bilgi_oyunu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_answer = update.message.text.strip().lower()
    correct_answer = bilgi_oyunu_games[chat_id]['answer'].lower()
    if user_answer == correct_answer:
        await update.message.reply_text("✅ Tebrikler, doğru cevap!")
    else:
        await update.message.reply_text(f"❌ Maalesef yanlış. Doğru cevap: {bilgi_oyunu_games[chat_id]['answer']}")
    del bilgi_oyunu_games[chat_id]

# --- BUL BAKALIM ---
WORDS = { "Elma": "Ağaçta yetişen, genellikle kırmızı veya yeşil renkli bir meyve.", "Gitar": "Telli bir müzik aleti.", "Yağmur": "Bulutlardan yeryüzüne düşen su damlaları.", "Saat": "Zamanı ölçmek için kullanılan bir alet.", "Futbol": "On birer kişilik iki takım arasında topla oynanan bir spor." }

async def start_bul_bakalim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if any(chat_id in g for g in [sayi_oyunu_games, hizli_mat_games, kelime_zinciri_games, plaka_oyunu_games, bayrak_oyunu_games, bilgi_oyunu_games, pi_oyunu_games, hafiza_simsegi_games, bosluk_doldurma_games]):
        await update.message.reply_text("Lütfen önce devam eden diğer oyunu bitirin.")
        return
        
    word, description = random.choice(list(WORDS.items()))
    bul_bakalim_games[chat_id] = {'answer': word}
    await update.message.reply_text(f"İpucu: {description}\n\nBu nedir? Bil bakalım!")

async def check_answer_bul_bakalim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_answer = update.message.text.strip().lower()
    correct_answer = bul_bakalim_games[chat_id]['answer'].lower()
    if user_answer == correct_answer:
        await update.message.reply_text(f"✅ Bravo! Doğru cevap: {bul_bakalim_games[chat_id]['answer']}")
        del bul_bakalim_games[chat_id]
    else:
        await update.message.reply_text("❌ Bilemedin, tekrar dene!")

# --- PI OYUNU ---
PI_START = "3.14159265358979323846"
async def start_pi_oyunu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if any(chat_id in g for g in [sayi_oyunu_games, hizli_mat_games, kelime_zinciri_games, plaka_oyunu_games, bayrak_oyunu_games, bilgi_oyunu_games, bul_bakalim_games, hafiza_simsegi_games, bosluk_doldurma_games]):
        await update.message.reply_text("Lütfen önce devam eden diğer oyunu bitirin.")
        return
        
    pi_oyunu_games[chat_id] = {'step': 0}
    await update.message.reply_text("Pi Oyunu başladı! Pi sayısının rakamlarını sırayla yazın.\nBaşlangıç için '3' yaz.")

async def check_digit_pi_oyunu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    game = pi_oyunu_games[chat_id]
    user_input = update.message.text.strip()
    expected_pi_string = PI_START.replace('.', '')
    
    if len(user_input) == 1 and user_input.isdigit() and user_input == expected_pi_string[game['step']]:
        game['step'] += 1
        await update.message.reply_text(f"✅ Doğru! {game['step']}. basamağa ulaştın. Sıradaki rakam?")
        if game['step'] == len(expected_pi_string):
             await update.message.reply_text("🎉 İnanılmaz! Bildiğim tüm basamakları tamamladın!")
             del pi_oyunu_games[chat_id]
    else:
        await update.message.reply_text(f"❌ Yanlış! {game['step']}. basamakta hata yaptın. Oyun bitti.")
        del pi_oyunu_games[chat_id]

# --- DOĞRULUK CESARET ---
TRUTHS = [ "En büyük sırrın ne?", "Hiç yalan söyledin mi?", "En utanç verici anın neydi?", "Birine söylediğin en kötü yalan neydi?", "Hayatında en çok pişman olduğun şey nedir?" ]
DARES = [ "Son aramanı herkese göster.", "Garip bir ses çıkar.", "Bir kaşık yoğurt ye.", "Telefonundaki son fotoğrafı göster.", "30 saniye boyunca plank yap." ]

async def start_dc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("Doğruluk"), KeyboardButton("Cesaret")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Doğruluk mu, cesaret mi?", reply_markup=reply_markup)

async def play_dc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.lower()
    if choice == "doğruluk":
        question = random.choice(TRUTHS)
        await update.message.reply_text(f"Doğruluk: {question}", reply_markup=None)
    elif choice == "cesaret":
        task = random.choice(DARES)
        await update.message.reply_text(f"Cesaret: {task}", reply_markup=None)

# --- HAFIZA ŞİMŞEĞİ ---
async def start_hafiza_simsegi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if any(chat_id in g for g in [sayi_oyunu_games, hizli_mat_games, kelime_zinciri_games, plaka_oyunu_games, bayrak_oyunu_games, bilgi_oyunu_games, bul_bakalim_games, pi_oyunu_games, bosluk_doldurma_games]):
        await update.message.reply_text("Lütfen önce devam eden diğer oyunu bitirin.")
        return

    number = str(random.randint(10000, 99999))
    hafiza_simsegi_games[chat_id] = {'answer': number}
    msg = await update.message.reply_text(f"Bu sayıyı aklında tut: **{number}**\nBu mesaj 3 saniye sonra silinecek.")
    await asyncio.sleep(3)
    await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
    await update.message.reply_text("Sayı neydi? Yaz bakalım.")

async def check_answer_hafiza_simsegi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_answer = update.message.text.strip()
    correct_answer = hafiza_simsegi_games[chat_id]['answer']
    if user_answer == correct_answer:
        await update.message.reply_text("🧠 Mükemmel hafıza! Tebrikler!")
    else:
        await update.message.reply_text(f"❌ Hatalı. Doğru sayı: {correct_answer}")
    del hafiza_simsegi_games[chat_id]

# --- BOŞLUK DOLDURMA ---
SENTENCES = { "Ayağını ____ göre uzat.": "yorganına", "Damlaya damlaya ____ olur.": "göl", "Gülü seven ____ katlanır.": "dikenine", "Sakla samanı, gelir ____.": "zamanı" }

async def start_bosluk_doldurma(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if any(chat_id in g for g in [sayi_oyunu_games, hizli_mat_games, kelime_zinciri_games, plaka_oyunu_games, bayrak_oyunu_games, bilgi_oyunu_games, bul_bakalim_games, pi_oyunu_games, hafiza_simsegi_games]):
        await update.message.reply_text("Lütfen önce devam eden diğer oyunu bitirin.")
        return
        
    sentence, answer = random.choice(list(SENTENCES.items()))
    bosluk_doldurma_games[chat_id] = {'answer': answer}
    await update.message.reply_text(f"Boşluğu doldur:\n\n{sentence}")

async def check_answer_bosluk_doldurma(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_answer = update.message.text.strip().lower()
    correct_answer = bosluk_doldurma_games[chat_id]['answer'].lower()
    if user_answer == correct_answer:
        await update.message.reply_text("✅ Harika! Doğru bildin.")
    else:
        await update.message.reply_text(f"❌ Olmadı. Doğru cevap: {bosluk_doldurma_games[chat_id]['answer']}")
    del bosluk_doldurma_games[chat_id]
    
# --- GELİŞTİRME AŞAMASINDAKİ OYUNLAR (PLACEHOLDER) ---
async def start_sudoku(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🧩 Sudoku oyunu şu anda geliştirme aşamasındadır.")

async def start_fark_bulmaca(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🖼️ Fark Bulmaca oyunu şu anda geliştirme aşamasındadır.")

async def start_kelime_anlatma(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🗣️ Kelime Anlatma oyunu şu anda geliştirme aşamasındadır.")

async def start_kelime_sarmali(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📜 Kelime Sarmalı oyunu şu anda geliştirme aşamasındadır.")


# --- 3. ANA BOT MANTIĞI ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot için başlangıç ve yardım mesajı gönderir."""
    help_text = (
        "Merhaba! Çok Oyunlu Bota Hoş Geldin!\n\n"
        "İşte oynayabileceğin oyunlar:\n"
        "/sayioyunu - Sıcak Soğuk Sayı Tahmini\n"
        "/matematik - Hızlı Matematik\n"
        "/kelimezinciri - Kelime Zinciri\n"
        "/plaka - Plaka Kodu Tahmini\n"
        "/bayrak - Bayrak Bilmece\n"
        "/bilgi - Genel Kültür Sorusu\n"
        "/bulbakalim - İpucundan Kelimeyi Bul\n"
        "/pi - Pi Sayısı Ezberleme Oyunu\n"
        "/dc - Doğruluk & Cesaret\n"
        "/hafiza - Hafıza Şimşeği\n"
        "/boslukdoldur - Atasözü Tamamlama\n\n"
        "--- Geliştiriliyor ---\n"
        "/sudoku - Sudoku\n"
        "/farkbul - Fark Bulmaca\n"
        "/kelimeanlat - Kelime Anlatma\n"
        "/kelimesarmali - Kelime Sarmalı\n\n"
        "Oyunları durdurmak için ilgili komutları kullanın (örn: /sayibitir)."
    )
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Komut olmayan mesajları aktif olan oyuna yönlendirir."""
    chat_id = update.effective_chat.id
    message_text = update.message.text

    if chat_id in sayi_oyunu_games:
        await guess_sayi_oyunu(update, context)
    elif chat_id in hizli_mat_games:
        await check_answer_hizli_matematik(update, context)
    elif chat_id in kelime_zinciri_games:
        await play_kelime_zinciri(update, context)
    elif chat_id in plaka_oyunu_games:
        await check_answer_plaka_oyunu(update, context)
    elif chat_id in bayrak_oyunu_games:
        await check_answer_bayrak_oyunu(update, context)
    elif chat_id in bilgi_oyunu_games:
        await check_answer_bilgi_oyunu(update, context)
    elif chat_id in bul_bakalim_games:
        await check_answer_bul_bakalim(update, context)
    elif chat_id in pi_oyunu_games:
        await check_digit_pi_oyunu(update, context)
    elif chat_id in hafiza_simsegi_games:
        await check_answer_hafiza_simsegi(update, context)
    elif chat_id in bosluk_doldurma_games:
        await check_answer_bosluk_doldurma(update, context)
    elif message_text and message_text.lower() in ["doğruluk", "cesaret"]:
        await play_dc(update, context)

def main():
    """Botu başlatır."""
    if BOT_TOKEN == "BURAYA_BOT_TOKENINI_YAPISTIR":
        print("HATA: Lütfen kodun içindeki BOT_TOKEN değişkenine kendi bot token'ınızı girin.")
        return
        
    application = Application.builder().token(BOT_TOKEN).build()

    # Genel komutlar
    application.add_handler(CommandHandler(["start", "help"], start_command))

    # Çalışan Oyun Komutları
    application.add_handler(CommandHandler("sayioyunu", start_sayi_oyunu))
    application.add_handler(CommandHandler("sayibitir", stop_sayi_oyunu))
    application.add_handler(CommandHandler("matematik", start_hizli_matematik))
    application.add_handler(CommandHandler("kelimezinciri", start_kelime_zinciri))
    application.add_handler(CommandHandler("zinciribitir", stop_kelime_zinciri))
    application.add_handler(CommandHandler("plaka", start_plaka_oyunu))
    application.add_handler(CommandHandler("bayrak", start_bayrak_oyunu))
    application.add_handler(CommandHandler("bilgi", start_bilgi_oyunu))
    application.add_handler(CommandHandler("bulbakalim", start_bul_bakalim))
    application.add_handler(CommandHandler("pi", start_pi_oyunu))
    application.add_handler(CommandHandler("dc", start_dc))
    application.add_handler(CommandHandler("hafiza", start_hafiza_simsegi))
    application.add_handler(CommandHandler("boslukdoldur", start_bosluk_doldurma))

    # Geliştirme Aşamasındaki Oyun Komutları
    application.add_handler(CommandHandler("sudoku", start_sudoku))
    application.add_handler(CommandHandler("farkbul", start_fark_bulmaca))
    application.add_handler(CommandHandler("kelimeanlat", start_kelime_anlatma))
    application.add_handler(CommandHandler("kelimesarmali", start_kelime_sarmali))

    # Komut olmayan tüm metin mesajları için genel işleyici
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Botu çalıştır
    print("Bot çalışıyor...")
    application.run_polling()

if __name__ == "__main__":
    main()
