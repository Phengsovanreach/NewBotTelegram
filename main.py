import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from downloader import download_video
from keep_alive import keep_alive

BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "👋 Welcome to Professional Downloader Bot\n\n"
        "Supported Platforms:\n"
        "🎬 YouTube\n"
        "📱 TikTok\n"
        "📘 Facebook\n"
        "📷 Instagram\n\n"
        "📥 Send me a video link to download."
    )

    await update.message.reply_text(text)


async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):

    url = update.message.text

    msg = await update.message.reply_text("⏳ Processing download...")

    try:

        file_path, title = download_video(url)

        await msg.edit_text("📤 Uploading video...")

        await update.message.reply_video(
            video=open(file_path, "rb"),
            caption=f"✅ {title}"
        )

        os.remove(file_path)

        await msg.delete()

    except Exception as e:

        await msg.edit_text(f"❌ Error:\n{str(e)}")


def main():

    keep_alive()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    print("🤖 Bot running...")

    app.run_polling()


if __name__ == "__main__":
    main()