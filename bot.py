from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yt_dlp
import os

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بيك\n\n"
        "🎧 تحميل صوت:\n"
        "/audio 128 <link>\n"
        "/audio 320 <link>\n\n"
        "🎬 تحميل فيديو:\n"
        "/video 360 <link>\n"
        "/video 720 <link>\n"
    )

async def audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        quality = context.args[0]
        url = context.args[1]

        ydl_opts = {
            "format": "bestaudio",
            "outtmpl": "audio.%(ext)s",
            "quiet": True,
        }

        await update.message.reply_text("⏳ جاري تحميل الصوت...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        file = [f for f in os.listdir() if f.startswith("audio.")][0]
        await update.message.reply_audio(open(file, "rb"))
        os.remove(file)

    except:
        await update.message.reply_text("❌ استخدم الأمر بالشكل الصح")

async def video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        quality = context.args[0]
        url = context.args[1]

        ydl_opts = {
            "format": f"bestvideo[height<={quality}]+bestaudio/best",
            "outtmpl": "video.mp4",
            "quiet": True,
        }

        await update.message.reply_text("⏳ جاري تحميل الفيديو...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        await update.message.reply_video(open("video.mp4", "rb"))
        os.remove("video.mp4")

    except:
        await update.message.reply_text("❌ استخدم الأمر بالشكل الصح")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("audio", audio))
app.add_handler(CommandHandler("video", video))

app.run_polling()
