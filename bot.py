from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
import yt_dlp
import os

TOKEN = os.environ.get("BOT_TOKEN")

# نخزن لينك كل مستخدم
user_links = {}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بيك\n\n"
        "📎 ابعت لينك الفيديو أو الأغنية\n"
        "(YouTube – Facebook – Instagram – TikTok – SoundCloud)"
    )

# استقبال اللينك
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user_links[update.effective_user.id] = url

    keyboard = [
        [
            InlineKeyboardButton("🎧 صوت", callback_data="choose_audio"),
            InlineKeyboardButton("🎬 فيديو", callback_data="choose_video"),
        ]
    ]

    await update.message.reply_text(
        "عايز تحمل إيه؟",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# اختيار صوت أو فيديو
async def choose_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "choose_audio":
        keyboard = [
            [
                InlineKeyboardButton("128 kbps", callback_data="audio_128"),
                InlineKeyboardButton("192 kbps", callback_data="audio_192"),
                InlineKeyboardButton("320 kbps ⭐", callback_data="audio_320"),
            ]
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton("360p", callback_data="video_360"),
                InlineKeyboardButton("720p", callback_data="video_720"),
                InlineKeyboardButton("1080p ⭐", callback_data="video_1080"),
            ]
        ]

    await query.edit_message_text(
        "اختار الجودة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# التحميل الفعلي
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    url = user_links.get(user_id)

    if not url:
        await query.edit_message_text("❌ ابعت اللينك الأول")
        return

    await query.edit_message_text("⏳ جاري التحميل...")

    try:
        # 🎧 تحميل صوت
        if query.data.startswith("audio"):
            ydl_opts = {
                "format": "bestaudio",
                "outtmpl": "%(title)s.%(ext)s",
                "noplaylist": True,
                "quiet": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            await query.message.reply_audio(
                audio=open(filename, "rb"),
                title=info.get("title")
            )

        # 🎬 تحميل فيديو (MP4 جاهز بدون ffmpeg)
        else:
            quality = query.data.split("_")[1]

            ydl_opts = {
                "format": f"best[ext=mp4][height<={quality}]/best[ext=mp4]",
                "outtmpl": "%(title)s.mp4",
                "noplaylist": True,
                "quiet": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            await query.message.reply_video(
                video=open(filename, "rb"),
                caption=info.get("title")
            )

        os.remove(filename)

    except Exception as e:
        await query.message.reply_text("❌ حصل خطأ أثناء التحميل")

# تشغيل البوت
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
app.add_handler(CallbackQueryHandler(choose_type, pattern="^choose_"))
app.add_handler(CallbackQueryHandler(download, pattern="^(audio|video)_"))

app.run_polling()
