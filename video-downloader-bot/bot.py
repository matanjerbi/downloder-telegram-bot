"""
בוט טלגרם להורדת סרטונים מכל פלטפורמה
משתמש ב-yt-dlp לתמיכה ביותר מ-1000 אתרים

נקודת כניסה ראשית
"""

import telebot

from config import BOT_TOKEN, DOWNLOADS_DIR
from utils.helpers import setup_logger, check_ffmpeg
from handlers import register_all_handlers

# הגדרת לוגר
logger = setup_logger(__name__)


def create_bot() -> telebot.TeleBot:
    """
    יצירת והגדרת הבוט

    Returns:
        אובייקט הבוט המוגדר
    """
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN לא הוגדר! צור קובץ .env עם הטוקן")
        exit(1)

    bot = telebot.TeleBot(BOT_TOKEN)
    register_all_handlers(bot)

    return bot


def main():
    """פונקציה ראשית להפעלת הבוט"""

    # בדיקת ffmpeg
    if not check_ffmpeg():
        logger.warning("ffmpeg לא מותקן! חלק מהפורמטים לא יעבדו")
        logger.warning("התקנה: brew install ffmpeg (Mac) / apt install ffmpeg (Linux)")

    # יצירת הבוט
    bot = create_bot()

    # ניקוי webhook ישן (אם קיים) - מונע שגיאת 409
    bot.remove_webhook()

    logger.info("הבוט מופעל...")
    logger.info(f"תיקיית הורדות: {DOWNLOADS_DIR}")

    # הפעלת הבוט
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60, allowed_updates=["message", "callback_query"])
    except Exception as e:
        logger.error(f"שגיאה בהפעלת הבוט: {e}")
        raise


if __name__ == '__main__':
    main()
