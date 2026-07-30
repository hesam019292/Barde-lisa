import json
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# ========== ۱. خواندن توکن ==========
# توکن مستقیماً از متغیرهای محیطی Railway خوانده می‌شود
TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise ValueError("❌ متغیر محیطی BOT_TOKEN تنظیم نشده است! لطفاً آن را در داشبورد Railway اضافه کنید.")

# ========== ۲. خواندن فایل JSON با مدیریت خطا ==========
try:
    with open("replies.json", "r", encoding="utf-8") as f:
        REPLIES = json.load(f)
    print(f"✅ تعداد پاسخ‌ها بارگذاری شد: {len(REPLIES)}")
except FileNotFoundError:
    print("❌ فایل replies.json پیدا نشد!")
    exit(1)
except json.JSONDecodeError as e:
    print(f"❌ خطا در سینتکس JSON: {e}")
    exit(1)

# ========== ۳. تابع اصلی پاسخ‌دهی ==========
async def smart_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # اگر پیام متنی نبود، بی‌خیال شو
    if not update.message or not update.message.text:
        return

    user_text = update.message.text.strip()
    chat_type = update.effective_chat.type
    bot_username = context.bot.username

    # ========== بررسی گروه ==========
    if chat_type in ("group", "supergroup"):
        # شرط ۱: آیا پیام ریپلای به بات است؟
        is_reply_to_bot = (
            update.message.reply_to_message and
            update.message.reply_to_message.from_user.id == context.bot.id
        )
        # شرط ۲: آیا منشن (@username) در متن وجود دارد؟
        is_mentioned = f"@{bot_username}" in user_text

        # اگر هیچکدام نبود، از تابع خارج شو (پاسخ نده)
        if not (is_reply_to_bot or is_mentioned):
            return

    # ========== پیدا کردن پاسخ مناسب ==========
    # مرتب‌سازی کلیدها از بلندترین به کوتاه‌ترین (اولویت با عبارت کامل‌تر)
    sorted_keys = sorted(REPLIES.items(), key=lambda x: len(x[0]), reverse=True)

    for trigger, response in sorted_keys:
        if trigger in user_text:
            await update.message.reply_text(response)
            break  # فقط به اولین تطبیق پاسخ بده

# ========== ۴. راه‌اندازی ربات ==========
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, smart_reply))

    print("🚀 ربات روشن شد و در حال گوش دادن است...")
    app.run_polling()

if __name__ == "__main__":
    main()
