import os
import asyncio
import logging
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

# --- ១. បង្កើត Web Server សម្រាប់ Render Free Tier ---
app_web = Flask('')

@app_web.route('/')
def home():
    return "🤖 Bot is running 24/7!"

def run_web():
    port = int(os.environ.get('PORT', 8080))
    app_web.run(host='0.0.0.0', port=port)

# --- ២. ការកំណត់ Bot ---
TOKEN = "8237446590:AAFUWWuMiPGmuAnK0n3oYxDzNlO08hqKPp0"
DOWNLOAD_DIR = "downloads"

if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 សួស្តី User! ផ្ញើ Link វីដេអូពី YouTube, TikTok ឬ Facebook មកខ្ញុំដើម្បីទាញយក។")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"):
        return

    status_msg = await update.message.reply_text("⏳ កំពុងដំណើរការ... សូមរង់ចាំ")

    # ការកំណត់ yt-dlp ថ្មីដើម្បីជៀសវាង Error Format
    ydl_opts = {
        # 'best' នឹងយក File ណាដែលមានទាំងរូប និងសំឡេងរួចជាស្រេច (មិនចាំបាច់ Merge)
        'format': 'best[ext=mp4]/best', 
        'outtmpl': f'{DOWNLOAD_DIR}/%(id)s.%(ext)s',
        'cookiefile': 'cookies.txt', 
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'noplaylist': True,
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            file_path = ydl.prepare_filename(info)

        await status_msg.edit_text("📤 កំពុងផ្ញើវីដេអូ...")
        
        with open(file_path, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file, 
                caption=f"✅ រួចរាល់៖\n🎬 {info.get('title', 'Video')}"
            )

        os.remove(file_path)

    except Exception as e:
        await update.message.reply_text(f"❌ កំហុស៖ {str(e)[:100]}")
    finally:
        try:
            await status_msg.delete()
        except:
            pass

def main():
    Thread(target=run_web).start()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    print("🚀 Bot is starting...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()