"""
הנדלר לזיהוי וטיפול בקישורים
"""
import uuid
import logging
from typing import Dict, Any

from telebot import TeleBot, types

from config import MESSAGES
from utils import extract_url
from utils.helpers import log_action

logger = logging.getLogger(__name__)

# מאגר זמני לשמירת מידע על סרטונים
video_cache: Dict[str, Dict[str, Any]] = {}


def get_cache() -> Dict[str, Dict[str, Any]]:
    """קבלת הקאש"""
    return video_cache


def register_url_handlers(bot: TeleBot) -> None:
    """
    רישום הנדלר לזיהוי קישורים

    Args:
        bot: אובייקט הבוט
    """

    @bot.message_handler(func=lambda m: m.text and extract_url(m.text) is not None)
    def handle_url(message: types.Message) -> None:
        """טיפול בקישור שנשלח"""
        url = extract_url(message.text)
        user_id = message.from_user.id

        log_action(logger, user_id, "URL_RECEIVED", url)

        # יצירת מפתח קאש מקוצר
        cache_key = uuid.uuid4().hex[:8]

        # שמירת URL מלא בקאש
        video_cache[cache_key] = {
            'url': url,
            'user_id': user_id
        }

        # יצירת כפתורים
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📊 פרטים", callback_data=f"info:{cache_key}"),
            types.InlineKeyboardButton("📥 הורדה", callback_data=f"download:{cache_key}")
        )

        bot.send_message(
            message.chat.id,
            MESSAGES['url_detected'],
            reply_markup=markup,
            reply_to_message_id=message.message_id
        )
