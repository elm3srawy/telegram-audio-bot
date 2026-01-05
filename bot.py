from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import yt_dlp
import os

TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بيك\n\n"
        "📎 ابعت أي لينك (YouTube / SoundCloud / غيره)\n"
        "وهيرجعلك الصوت بصيغة m4a ويتسمع فورًا 🎧"
    )

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("⏳ جاري تحميل الصوت...")

    try:
        ydl_opts = {
            # نفضل m4a دايمًا
            "format": "bestaudio[ext=m4a]/bestaudio",
            "outtmpl": "%(title)s.%(ext)s",
            "noplaylist": True,
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        # إرسال الصوت (Streaming)
        await update.message.reply_audio(
            audio=open(filename, "rb"),
            title=info.get("title"),
        )

        os.remove(filename)

    except Exception:
        await update.message.reply_text("❌ حصل خطأ في تحميل الصوت")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

app.run_polling()
