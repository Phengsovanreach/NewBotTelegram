import os
import asyncio
import logging
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

# --- ១. បង្កើត Web Server តូចមួយដើម្បីឱ្យ Render Free Tier ដំណើរការ ---
app_web = Flask('')

@app_web.route('/')
def home():
    return "🤖 Bot is running 24/7!"

def run_web():
    # Render នឹងផ្ដល់ Port ឱ្យយើងដោយស្វ័យប្រវត្តិ
    port = int(os.environ.get('PORT', 8080))
    app_web.run(host='0.0.0.0', port=port)

# --- ២. ការកំណត់ Bot ---
# ប្រើ Token របស់ Morgan
TOKEN = "8237446590:AAFUWWuMiPGmuAnK0n3oYxDzNlO08hqKPp0"
DOWNLOAD_DIR = "downloads"

# បង្កើត Folder សម្រាប់ទុកវីដេអូបណ្ដោះអាសន្ន
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 សួស្តី User! ផ្ញើ Link វីដេអូពី YouTube, TikTok ឬ Facebook មកខ្ញុំដើម្បីទាញយក។")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"):
        return

    status_msg = await update.message.reply_text("⏳ កំពុងត្រួតពិនិត្យ និងទាញយក... សូមរង់ចាំបន្តិច")

    # ការកំណត់ yt-dlp ឱ្យដើរជាមួយ Cookies និងកំណត់ទំហំឱ្យត្រូវនឹង Telegram
    ydl_opts = {
        # កំណត់យកត្រឹម 720p ដើម្បីកុំឱ្យលើស 50MB (Telegram Limit)
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(id)s.%(ext)s',
        'cookiefile': 'cookies.txt',  # ប្រើឯកសារដែល Morgan ទើបតែប្តូរមិញ
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'noplaylist': True,
        'quiet': True,
        'merge_output_format': 'mp4',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ប្រើ run_in_executor ដើម្បីកុំឱ្យ Bot គាំងពេលកំពុង Download
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
            file_path = ydl.prepare_filename(info)

        await status_msg.edit_text("📤 កំពុងផ្ញើវីដេអូទៅកាន់អ្នក...")
        
        with open(file_path, 'rb') as video_file:
            await update.message.reply_video(
                video=video_file, 
                caption=f"✅ ទាញយកជោគជ័យ៖\n🎬 {info.get('title', 'Video')}"
            )

        # លុបវីដេអូចេញពី Server ក្រោយផ្ញើរួចដើម្បីសន្សំទំហំ
        os.remove(file_path)

    except Exception as e:
        error_text = str(e)
        if "Sign in" in error_text:
            await update.message.reply_text("❌ YouTube ប្លុក IP ។ សូមពិនិត្យមើល cookies.txt ម្ដងទៀត។")
        else:
            await update.message.reply_text(f"❌ កើតមានកំហុស៖ {error_text[:100]}")
    finally:
        try:
            await status_msg.delete()
        except:
            pass

def main():
    # បើក Web Server នៅ Background
    Thread(target=run_web).start()

    # ដំណើរការ Telegram Bot
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("🚀 Bot is starting on Render Free Tier...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()