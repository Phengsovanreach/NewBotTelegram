import os
import yt_dlp
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# =========================
# TELEGRAM BOT TOKEN
# =========================
BOT_TOKEN = "8237446590:AAFUWWuMiPGmuAnK0n3oYxDzNlO08hqKPp0"

DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# =========================
# KEEP BOT ALIVE FOR RENDER
# =========================
app_web = Flask('')

@app_web.route('/')
def home():
    return "🤖 Bot is running!"

def run_web():
    app_web.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# =========================
# START COMMAND
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "👋 Welcome to Downloader Bot\n\n"
        "Send a link from:\n"
        "• YouTube\n"
        "• TikTok\n"
        "• Facebook\n\n"
        "📥 I will download the video for you."
    )

    await update.message.reply_text(text)

# =========================
# DOWNLOAD FUNCTION
# =========================
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text

    msg = await update.message.reply_text("⏳ Processing...")

    try:

        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'format': 'best',
            'cookiefile': 'cookies.txt'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        await msg.edit_text("📤 Uploading...")

        await update.message.reply_video(video=open(file_path, "rb"))

        os.remove(file_path)

        await msg.delete()

    except Exception as e:
        await msg.edit_text(f"❌ Error: {e}")

# =========================
# MAIN
# =========================
def main():

    keep_alive()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))

    print("🤖 Bot started...")

    app.run_polling()

if __name__ == "__main__":
    main()