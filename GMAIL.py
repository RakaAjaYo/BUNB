import smtplib
import logging
import asyncio
import requests
import datetime
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Konfigurasi logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Konfigurasi Bot Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', "TOKEN_BOT_ANDA_DISINI")
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', "WEATHER_API_KEY_ANDA")

# Konfigurasi Email
sender_email = "senijil243@usiver.com"
receiver_emails = [
    "support@whatsapp.com", "Android@whatsapp.com", "smb@support.whatsapp.com",
    "business_web@support.whatsapp.com", "webclient_web@support.whatsapp.com",
    "iphone_web@support.whatsapp.com", "android_web@support.whatsapp.com",
    "phish@meta.com", "report@meta.com", "security@meta.com", "abuse@meta.com",
    "support@whatsapp.com", "abuse@whatsapp.com", "privacy@whatsapp.com",
    "phish@whatsapp.com", "support@meta.com", "security@whatsapp.com", "info@whatsapp.com"
]

# State management untuk tracking user
user_states = {}
user_data_store = {}

# Video configuration
VIDEO_FILE = "VIDEO_HOZOO.mp4"

def get_current_weather(location="Jakarta"):
    """Mendapatkan data cuaca saat ini dari OpenWeatherMap API :cite[3]:cite[6]"""
    try:
        # First get coordinates from location name
        geocoder_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={WEATHER_API_KEY}"
        geo_response = requests.get(geocoder_url)
        geo_data = geo_response.json()
        
        if not geo_data:
            return None
            
        lat = geo_data[0]['lat']
        lon = geo_data[0]['lon']
        
        # Get weather data
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric&lang=id"
        response = requests.get(weather_url)
        weather_data = response.json()
        
        return {
            'temperature': weather_data['main']['temp'],
            'description': weather_data['weather'][0]['description'],
            'humidity': weather_data['main']['humidity'],
            'wind_speed': weather_data['wind']['speed'],
            'clouds': weather_data['clouds']['all'],
            'location': location
        }
    except Exception as e:
        print(f"Error getting weather: {e}")
        return None

def get_current_datetime():
    """Mendapatkan informasi tanggal dan waktu saat ini :cite[5]"""
    now = datetime.datetime.now()
    return {
        'hari': now.strftime("%A"),
        'tanggal': now.strftime("%d %B %Y"),
        'jam': now.strftime("%H:%M:%S"),
        'bulan': now.strftime("%B"),
        'tahun': now.strftime("%Y")
    }

def send_email_async(phone_number):
    """Fungsi untuk mengirim email di background thread"""
    def send_email():
        try:
            subject = "Request for Permanent Unban of WhatsApp Number Due to Violation"
            body = f"""
Dear WhatsApp Support Team,

I am writing to request the permanent unbanning of my WhatsApp number, {phone_number} which was banned due to a violation of WhatsApp's terms of service. 

I acknowledge the mistake and sincerely apologize for any inconvenience caused. I assure you that I understand the importance of adhering to the platform's guidelines and am committed to using WhatsApp responsibly in the future. 

I kindly ask for your understanding and consideration in granting me a second chance to regain access to my account. 

Thank you for your attention to this matter.

Sincerely,
WhatsApp User
Phone: {phone_number}
"""

            # Membuat email
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = ", ".join(receiver_emails)
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Mengirim email melalui SMTP :cite[7]
            server = smtplib.SMTP('smtp.usiver.com', 587)
            server.ehlo()
            server.starttls()  # Enkripsi koneksi :cite[7]
            server.ehlo()
            
            password = "password_anda_disini"  # Ganti dengan password email Anda
            
            server.login(sender_email, password)
            text = msg.as_string()
            
            # Kirim ke semua penerima
            for receiver in receiver_emails:
                server.sendmail(sender_email, receiver, text)
            
            server.quit()
            print(f"Email berhasil dikirim untuk nomor {phone_number}")
            
        except Exception as e:
            print(f"Gagal mengirim email: {str(e)}")

    # Jalankan di thread terpisah
    thread = Thread(target=send_email)
    thread.start()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /start - Menampilkan menu utama dengan video :cite[4]"""
    user_id = update.effective_user.id
    user_states[user_id] = "MAIN_MENU"
    
    # Kirim video terlebih dahulu :cite[4]
    try:
        with open(VIDEO_FILE, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption="🎬 **Selamat Datang di Bot Unban WhatsApp!**\n\nVideo pembuka yang keren untuk Anda!",
                supports_streaming=True
            )
    except FileNotFoundError:
        await update.message.reply_text("⚠️ Video tidak ditemukan, melanjutkan tanpa video...")
    
    # Dapatkan informasi waktu dan cuaca
    datetime_info = get_current_datetime()
    weather_info = get_current_weather()
    
    # Buat pesan sambuatan dengan informasi real-time
    welcome_message = (
        f"🤖 **Bot Unban WhatsApp**\n\n"
        f"🕐 **Waktu Saat Ini:**\n"
        f"• Hari: {datetime_info['hari']}\n"
        f"• Tanggal: {datetime_info['tanggal']}\n"
        f"• Jam: {datetime_info['jam']}\n"
    )
    
    if weather_info:
        welcome_message += (
            f"\n🌤️ **Informasi Cuaca ({weather_info['location']}):**\n"
            f"• Suhu: {weather_info['temperature']}°C\n"
            f"• Deskripsi: {weather_info['description']}\n"
            f"• Kelembaban: {weather_info['humidity']}%\n"
            f"• Awan: {weather_info['clouds']}%\n"
            f"• Angin: {weather_info['wind_speed']} m/s"
        )
    
    welcome_message += (
        f"\n\n**Fitur Tersedia:**\n"
        f"• /phone 📱 - Ajukan unban WhatsApp\n"
        f"• /info ℹ️ - Info waktu & cuaca real-time\n"
        f"• /unlimited 🔄 - Mode unlimited\n"
        f"• /help ❓ - Bantuan\n"
        f"• /about ℹ️ - Tentang bot"
    )
    
    # Buat keyboard menu
    keyboard = [
        [KeyboardButton("/phone 📱"), KeyboardButton("/info ℹ️")],
        [KeyboardButton("/unlimited 🔄"), KeyboardButton("/help ❓")],
        [KeyboardButton("/about ℹ️")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /info - Menampilkan info waktu dan cuaca real-time"""
    datetime_info = get_current_datetime()
    weather_info = get_current_weather()
    
    info_message = (
        f"📊 **Informasi Real-Time**\n\n"
        f"🕐 **Waktu Saat Ini:**\n"
        f"• Hari: {datetime_info['hari']}\n"
        f"• Tanggal: {datetime_info['tanggal']}\n"
        f"• Jam: {datetime_info['jam']}\n"
        f"• Bulan: {datetime_info['bulan']}\n"
        f"• Tahun: {datetime_info['tahun']}\n"
    )
    
    if weather_info:
        # Tentukan emoji berdasarkan kondisi cuaca
        weather_emoji = "🌤️"
        if "hujan" in weather_info['description'].lower():
            weather_emoji = "🌧️"
        elif "cerah" in weather_info['description'].lower():
            weather_emoji = "☀️"
        elif "mendung" in weather_info['description'].lower():
            weather_emoji = "☁️"
        
        info_message += (
            f"\n{weather_emoji} **Informasi Cuaca ({weather_info['location']}):**\n"
            f"• Suhu: {weather_info['temperature']}°C\n"
            f"• Deskripsi: {weather_info['description']}\n"
            f"• Kelembaban: {weather_info['humidity']}%\n"
            f"• Awan: {weather_info['clouds']}%\n"
            f"• Angin: {weather_info['wind_speed']} m/s"
        )
    else:
        info_message += "\n⚠️ **Cuaca:** Data cuaca tidak tersedia sementara"
    
    await update.message.reply_text(info_message, parse_mode='HTML')

async def unlimited_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /unlimited - Mode unlimited"""
    user_id = update.effective_user.id
    user_states[user_id] = "UNLIMITED_MODE"
    
    await update.message.reply_text(
        "🔄 **Mode Unlimited Diaktifkan!**\n\n"
        "Bot akan mengirim informasi real-time secara terus menerus.\n"
        "Ketik 'stop' untuk menghentikan mode unlimited.\n\n"
        "Memulai pengiriman unlimited..."
    )
    
    # Mulai pengiriman unlimited
    asyncio.create_task(send_unlimited_updates(update, context))

async def send_unlimited_updates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mengirim update unlimited dengan informasi real-time"""
    user_id = update.effective_user.id
    message_count = 0
    
    while user_states.get(user_id) == "UNLIMITED_MODE" and message_count < 50:  # Safety limit
        try:
            datetime_info = get_current_datetime()
            weather_info = get_current_weather()
            
            update_message = (
                f"🔄 **Update #{message_count + 1}**\n"
                f"🕐 {datetime_info['jam']} | {datetime_info['tanggal']}\n"
            )
            
            if weather_info and message_count % 5 == 0:  # Update cuaca setiap 5 pesan
                update_message += (
                    f"🌤️ Cuaca: {weather_info['temperature']}°C, {weather_info['description']}\n"
                    f"☁️ Awan: {weather_info['clouds']}% | 💨 Angin: {weather_info['wind_speed']} m/s"
                )
            
            await update.message.reply_text(update_message)
            message_count += 1
            await asyncio.sleep(10)  # Kirim setiap 10 detik
            
        except Exception as e:
            print(f"Error in unlimited updates: {e}")
            break
    
    if user_states.get(user_id) == "UNLIMITED_MODE":
        user_states[user_id] = "MAIN_MENU"
        await update.message.reply_text("🛑 **Mode Unlimited Dihentikan** (batas maksimal tercapai)")

async def phone_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /phone - Meminta nomor telepon"""
    user_id = update.effective_user.id
    user_states[user_id] = "AWAITING_PHONE"
    
    await update.message.reply_text(
        "📱 **Masukkan Nomor WhatsApp**\n\n"
        "Silakan masukkan nomor WhatsApp yang ingin diajukan unban dalam format internasional:\n"
        "Contoh: +6281234567890\n\n"
        "Ketik 'batal' untuk membatalkan."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk pesan teks biasa"""
    user_id = update.effective_user.id
    text = update.message.text
    
    # Handle stop command untuk unlimited mode
    if text.lower() == 'stop' and user_states.get(user_id) == "UNLIMITED_MODE":
        user_states[user_id] = "MAIN_MENU"
        await update.message.reply_text("🛑 **Mode Unlimited Dihentikan**")
        return
    
    if user_states.get(user_id) == "AWAITING_PHONE":
        # Validasi nomor telepon
        if text.lower() == 'batal':
            user_states[user_id] = "MAIN_MENU"
            await update.message.reply_text("❌ Proses dibatalkan.")
            return
        
        # Validasi sederhana untuk nomor telepon
        if text.startswith('+') and len(text) > 10:
            # Simpan data user
            user_data_store[user_id] = {"phone": text}
            
            # Kirim konfirmasi
            keyboard = [[KeyboardButton("Ya ✅"), KeyboardButton("Tidak ❌")]]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                f"📋 **Konfirmasi Data**\n\n"
                f"Nomor WhatsApp: {text}\n\n"
                f"Apakah data sudah benar?",
                reply_markup=reply_markup
            )
            user_states[user_id] = "CONFIRMATION"
            
        else:
            await update.message.reply_text(
                "❌ Format nomor tidak valid!\n"
                "Gunakan format internasional dengan kode negara:\n"
                "Contoh: +6281234567890\n\n"
                "Silakan coba lagi atau ketik 'batal' untuk membatalkan."
            )
    
    elif user_states.get(user_id) == "CONFIRMATION":
        if text.lower() in ['ya', 'ya ✅']:
            # Proses pengiriman email
            phone_number = user_data_store[user_id]["phone"]
            
            await update.message.reply_text("⏳ Mengirim permohonan unban...")
            
            # Kirim email di background
            send_email_async(phone_number)
            
            # Reset state
            user_states[user_id] = "MAIN_MENU"
            
            await update.message.reply_text(
                f"✅ **Permohonan Terkirim!**\n\n"
                f"Nomor: {phone_number}\n"
                f"Permohonan unban telah dikirim ke tim support WhatsApp.\n"
                f"Biasanya membutuhkan waktu 24-48 jam untuk verifikasi.\n\n"
                f"Gunakan /phone untuk mengajukan nomor lain."
            )
            
        elif text.lower() in ['tidak', 'tidak ❌']:
            user_states[user_id] = "AWAITING_PHONE"
            await update.message.reply_text(
                "Silakan masukkan ulang nomor WhatsApp:\n"
                "Contoh: +6281234567890\n\n"
                "Ketik 'batal' untuk membatalkan."
            )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /help"""
    await update.message.reply_text(
        "❓ **Bantuan Penggunaan**\n\n"
        "**Cara menggunakan bot:**\n"
        "• /start - Memulai bot dengan video\n"
        "• /phone - Ajukan unban WhatsApp\n"
        "• /info - Info waktu & cuaca real-time\n"
        "• /unlimited - Mode update terus menerus\n"
        "• /help - Bantuan ini\n\n"
        "**Format nomor:** +6281234567890\n"
        "**Mode Unlimited:** Kirim 'stop' untuk berhenti"
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /about"""
    await update.message.reply_text(
        "ℹ️ **Tentang Bot**\n\n"
        "🤖 Bot Unban WhatsApp Premium\n"
        "Versi: 2.0\n\n"
        "**Fitur Baru:**\n"
        "• Video pembuka keren\n"
        "• Informasi waktu real-time\n"
        "• Data cuaca dan awan\n"
        "• Mode unlimited updates\n"
        "• Tampilan HD\n\n"
        "Dibuat dengan Python dan python-telegram-bot library."
    )

def main():
    """Fungsi utama untuk menjalankan bot"""
    # Buat application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("phone", phone_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("unlimited", unlimited_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Jalankan bot
    print("Bot sedang berjalan...")
    application.run_polling()

if __name__ == "__main__":
    main()
