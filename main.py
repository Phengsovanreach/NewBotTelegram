import os
import asyncio
import logging
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

# --- Web Server សម្រាប់ Render Free Tier ---
app_web = Flask('')
@app_web.route('/')
def home():
    return "Bot is alive!"

def run_web():
    port = int(os.environ.get('PORT', 8080))
    app_web.run(host='0.0.0.0', port=port)

# --- ការកំណត់ Bot ---
TOKEN = "8237446590:AAFUWWuMiPGmuAnK0n3oYxDzNlO08hqKPp0"
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 សួស្តី User ផ្ញើ Link វីដេអូ (YouTube/TikTok/FB) មកខ្ញុំ។")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"): return

    status = await update.message.reply_text("⏳ កំពុងដំណើរការ... សូមរង់ចាំ")
    
    # កំណត់ Option ឱ្យទន់ភ្លន់បំផុតដើម្បីកុំឱ្យជាប់ Error Format
    ydl_opts = {
        'format': 'best', # យកអាណាដែលដើរល្អបំផុត
        'outtmpl': f'{DOWNLOAD_DIR}/%(id)s.%(ext)s',
        'cookiefile': 'cookies.txt', # ត្រូវ Upload cookies.txt ទៅ GitHub ផង
        'noplaylist': True,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            file_path = ydl.prepare_filename(info)

        await status.edit_text("📤 កំពុងផ្ញើវីដេអូ...")
        with open(file_path, 'rb') as video:
            await update.message.reply_video(video=video, caption=f"✅ {info.get('title', 'Video')}")
        
        os.remove(file_path) # លុបចេញដើម្បីកុំឱ្យពេញ Server
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)[:100]}")
    finally:
        try: await status.delete()
        except: pass

def main():
    Thread(target=run_web).start() # បើក Web Server
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    print("🚀 Bot is running on Render Free Tier!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()