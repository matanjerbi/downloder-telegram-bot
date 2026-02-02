"""
בוט טלגרם להורדת סרטונים מכל פלטפורמה
משתמש ב-yt-dlp לתמיכה ביותר מ-1000 אתרים

נקודת כניסה ראשית
"""

import os
import base64

import telebot

from config import BOT_TOKEN, DOWNLOADS_DIR, COOKIES_FILE
from utils.helpers import setup_logger, check_ffmpeg
from handlers import register_all_handlers

# הגדרת לוגר
logger = setup_logger(__name__)


# === Optional Cookie Setup ===
def setup_cookies() -> bool:
    """
    יוצר קובץ cookies.txt מהמשתנה סביבה אם קיים.
    אם לא קיים - הבוט ממשיך לעבוד בלי cookies (רלוונטי ל-Render בלבד)
    """
    cookies_base64 = os.getenv('YOUTUBE_COOKIES_BASE64')

    if cookies_base64:
        try:
            # המרה מbase64 לטקסט רגיל
            cookies_content = base64.b64decode(cookies_base64).decode('utf-8')

            # יצירת הקובץ בנתיב הנכון
            with open(COOKIES_FILE, 'w') as f:
                f.write(cookies_content)

            logger.info("YouTube Cookies נוצרו מהמשתנה סביבה (נדרש ל-Render)")
            return True

        except Exception as e:
            logger.error(f"שגיאה ביצירת cookies: {e}")
            logger.warning("ממשיך בלי cookies - YouTube עלול לא לעבוד")
            return False
    else:
        # אין משתנה סביבה - זה OK! (מצב לוקאלי)
        logger.info("אין משתנה YOUTUBE_COOKIES_BASE64 - רץ במצב רגיל")
        return False


# הפעלת setup של cookies
setup_cookies()


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
