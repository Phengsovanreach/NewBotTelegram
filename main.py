import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import yt_dlp

# ---------------- CONFIG ----------------
TOKEN = "8237446590:AAFUWWuMiPGmuAnK0n3oYxDzNlO08hqKPp0"

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ---------------- COMMAND ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Hello!\n"
        "Send me a video link (YouTube / TikTok / Facebook)."
    )

# ---------------- DOWNLOAD FUNCTION ----------------
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text
    status = await update.message.reply_text("⬇️ Downloading...")

    filename = None

    ydl_opts = {
        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
        "format": "best",
        "quiet": True,
        "restrictfilenames": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await status.edit_text("📤 Uploading...")

        with open(filename, "rb") as video:
            await update.message.reply_video(video=video, caption="✅ Done!")

    except Exception as e:
        await update.message.reply_text(f"❌ Error:\n{e}")

    finally:
        if filename and os.path.exists(filename):
            os.remove(filename)

        await status.delete()

# ---------------- MAIN ----------------
def main():

    print("🤖 Bot started...")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    app.run_polling()

if __name__ == "__main__":
    main()