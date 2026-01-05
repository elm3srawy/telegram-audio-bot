from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yt_dlp
import os

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بيك\n\n"
        "🎧 تحميل صوت:\n"
        "/audio <link>\n\n"
        "🎬 تحميل فيديو:\n"
        "/video 360 <link>\n"
        "/video 720 <link>\n"
    )

async def audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = context.args[0]

        ydl_opts = {
            "format": "bestaudio",
            "outtmpl": "%(title)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
        }

        await update.message.reply_text("⏳ جاري تحميل الصوت...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await update.message.reply_audio(
            audio=open(filename, "rb"),
            title=info.get("title"),
        )

        os.remove(filename)

    except Exception as e:
        await update.message.reply_text("❌ حصل خطأ في تحميل الصوت")

async def video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        quality = context.args[0]
        url = context.args[1]

        ydl_opts = {
            "format": f"bestvideo[height<={quality}]+bestaudio/best",
            "outtmpl": "%(title)s.mp4",
            "quiet": True,
            "noplaylist": True,
        }

        await update.message.reply_text("⏳ جاري تحميل الفيديو...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        await update.message.reply_video(
            video=open(filename, "rb"),
            caption=info.get("title"),
        )

        os.remove(filename)

    except Exception:
        await update.message.reply_text("❌ استخدم الأمر بالشكل الصح")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("audio", audio))
app.add_handler(CommandHandler("video", video))

app.run_polling()
