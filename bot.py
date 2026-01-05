from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import yt_dlp
import os
import glob

TOKEN = os.environ.get("BOT_TOKEN")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat_id

    ydl_opts = {
        "format": "bestaudio",
        "outtmpl": "audio.%(ext)s",
        "noplaylist": True,
        "quiet": True,
    }

    await update.message.reply_text("⏳ جاري تحميل الصوت...")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        file = glob.glob("audio.*")[0]

        await context.bot.send_audio(
            chat_id=chat_id,
            audio=open(file, "rb")
        )

        os.remove(file)

    except Exception as e:
        await update.message.reply_text("❌ حصل خطأ أثناء التحميل")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

app.run_polling()
