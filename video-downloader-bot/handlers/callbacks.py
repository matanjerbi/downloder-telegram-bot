"""
הנדלרים ל-callback queries (לחיצות על כפתורים)
"""
import threading
import os
import time
import logging

from telebot import TeleBot, types

from config import MESSAGES, MAX_FILE_SIZE
from services import (
    get_video_info,
    get_available_qualities,
    download_video,
    PrivateContentError
)
from services.video_info import format_video_details
from utils import cleanup_file, format_size, extract_url
from utils.helpers import log_action
from handlers.url import get_cache

logger = logging.getLogger(__name__)


def _get_url_from_cache_key(cache_key: str) -> str:
    """
    קבלת URL מהקאש או ישירות מהמפתח

    אם הקאש ריק (למשל אחרי restart), ננסה להשתמש
    במפתח עצמו כ-URL (עובד לקישורים קצרים מ-60 תווים)

    Args:
        cache_key: מפתח הקאש (יכול להיות URL מקוצר)

    Returns:
        URL מלא או None אם לא תקין
    """
    video_cache = get_cache()

    # אם יש בקאש - נשתמש בזה
    if cache_key in video_cache:
        return video_cache[cache_key]['url']

    # אם המפתח עצמו הוא URL תקין - נשתמש בו ונוסיף לקאש
    if cache_key.startswith('http') and extract_url(cache_key):
        video_cache[cache_key] = {'url': cache_key}
        return cache_key

    return None


def register_callback_handlers(bot: TeleBot) -> None:
    """
    רישום הנדלרים ל-callbacks

    Args:
        bot: אובייקט הבוט
    """

    @bot.callback_query_handler(func=lambda call: call.data.startswith('info:'))
    def handle_info_callback(call: types.CallbackQuery) -> None:
        """טיפול בבקשת פרטים"""
        cache_key = call.data[5:]
        user_id = call.from_user.id
        video_cache = get_cache()

        # ניסיון לקבל URL מהקאש או מהמפתח
        url = _get_url_from_cache_key(cache_key)
        if not url:
            bot.answer_callback_query(call.id, MESSAGES['link_expired'])
            return

        log_action(logger, user_id, "INFO_REQUEST", url)

        # עדכון הודעה
        bot.edit_message_text(
            MESSAGES['fetching_info'],
            call.message.chat.id,
            call.message.message_id
        )

        try:
            info = get_video_info(url)

            if not info:
                bot.edit_message_text(
                    MESSAGES['error_no_video'],
                    call.message.chat.id,
                    call.message.message_id
                )
                return

            # שמירת מידע בקאש
            if cache_key in video_cache:
                video_cache[cache_key]['info'] = info

            # בניית הודעת פרטים
            details_text = format_video_details(info)

            # כפתורי פעולה
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("📥 הורדה", callback_data=f"download:{cache_key}"),
                types.InlineKeyboardButton("❌ סגור", callback_data="close")
            )

            bot.edit_message_text(
                details_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=markup
            )

        except PrivateContentError:
            bot.edit_message_text(
                MESSAGES['error_private'],
                call.message.chat.id,
                call.message.message_id
            )
        except Exception as e:
            logger.error(f"שגיאה בקבלת פרטים: {e}")
            bot.edit_message_text(
                MESSAGES['error_not_supported'],
                call.message.chat.id,
                call.message.message_id
            )

        bot.answer_callback_query(call.id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('download:'))
    def handle_download_callback(call: types.CallbackQuery) -> None:
        """טיפול בבקשת הורדה - הצגת בחירת איכות"""
        cache_key = call.data[9:]
        user_id = call.from_user.id
        video_cache = get_cache()

        # ניסיון לקבל URL מהקאש או מהמפתח
        url = _get_url_from_cache_key(cache_key)
        if not url:
            bot.answer_callback_query(call.id, MESSAGES['link_expired'])
            return

        log_action(logger, user_id, "DOWNLOAD_REQUEST", url)

        # בדיקה אם יש כבר מידע בקאש
        info = video_cache.get(cache_key, {}).get('info')

        if not info:
            bot.edit_message_text(
                MESSAGES['fetching_info'],
                call.message.chat.id,
                call.message.message_id
            )

            try:
                info = get_video_info(url)
                if cache_key in video_cache:
                    video_cache[cache_key]['info'] = info
            except PrivateContentError:
                bot.edit_message_text(
                    MESSAGES['error_private'],
                    call.message.chat.id,
                    call.message.message_id
                )
                bot.answer_callback_query(call.id)
                return
            except Exception as e:
                logger.error(f"שגיאה: {e}")
                bot.edit_message_text(
                    MESSAGES['error_not_supported'],
                    call.message.chat.id,
                    call.message.message_id
                )
                bot.answer_callback_query(call.id)
                return

        # קבלת איכויות זמינות
        qualities = get_available_qualities(info)

        if not qualities:
            _start_download(bot, call, cache_key, url, 'best', False)
            bot.answer_callback_query(call.id)
            return

        # יצירת כפתורי איכות
        markup = _create_quality_buttons(cache_key, qualities)

        bot.edit_message_text(
            MESSAGES['select_quality'],
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )

        bot.answer_callback_query(call.id)



    @bot.callback_query_handler(func=lambda call: call.data.startswith('quality:'))
    def handle_quality_callback(call: types.CallbackQuery) -> None:
        """טיפול בבחירת איכות"""

        try:
            # פירוס בטוח – ה-URL עלול להכיל נקודותיים
            _, rest = call.data.split(':', 1)
            cache_key, quality = rest.rsplit(':', 1)

            # ניסיון לקבל URL
            url = _get_url_from_cache_key(cache_key)
            if not url:
                bot.answer_callback_query(call.id, MESSAGES['link_expired'], show_alert=True)
                return

            audio_only = (quality == 'audio')

            # ✨ הכי חשוב – עונים ל-callback מיד
            bot.answer_callback_query(call.id, "מתחיל הורדה ⏳")

            # מריצים הורדה ב-thread נפרד (לא חוסם את הבוט)
            threading.Thread(
                target=_start_download,
                args=(bot, call, cache_key, url, quality, audio_only),
                daemon=True
            ).start()

        except Exception as e:
            logger.error(f"שגיאה בבחירת איכות: {e}", exc_info=True)
            bot.answer_callback_query(call.id, MESSAGES['error_download'], show_alert=True)



def _create_quality_buttons(cache_key: str, qualities: list) -> types.InlineKeyboardMarkup:
    """
    יצירת כפתורי בחירת איכות

    Args:
        cache_key: מפתח הקאש
        qualities: רשימת איכויות

    Returns:
        Markup עם הכפתורים
    """
    markup = types.InlineKeyboardMarkup(row_width=2)
    quality_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣']
    buttons = []

    for i, q in enumerate(qualities):
        if q.get('audio_only'):
            label = "🎵 אודיו בלבד"
            callback = f"quality:{cache_key}:audio"
        else:
            label = f"{quality_emojis[i]} {q['label']}"
            callback = f"quality:{cache_key}:{q['height']}"

        buttons.append(types.InlineKeyboardButton(label, callback_data=callback))

    # הוספת כפתורים בשורות של 2
    for i in range(0, len(buttons), 2):
        row = buttons[i:i + 2]
        markup.add(*row)

    # כפתור ביטול
    markup.add(types.InlineKeyboardButton("❌ ביטול", callback_data="close"))

    return markup


def _start_download(bot: TeleBot, call: types.CallbackQuery,
                    cache_key: str, url: str, quality: str, audio_only: bool) -> None:
    """
    התחלת הורדה ושליחת הקובץ

    Args:
        bot: אובייקט הבוט
        call: ה-callback query
        cache_key: מפתח הקאש
        url: הקישור להורדה
        quality: איכות נבחרת
        audio_only: האם אודיו בלבד
    """
    user_id = call.from_user.id
    filepath = None

    log_action(logger, user_id, "DOWNLOAD_START", f"URL: {url}, Quality: {quality}")

    start_time = time.time()

    # עדכון סטטוס
    bot.edit_message_text(
        MESSAGES['downloading'],
        call.message.chat.id,
        call.message.message_id
    )

    try:
        # הורדה
        filepath = download_video(url, quality, audio_only)

        if not filepath or not os.path.exists(filepath):
            bot.edit_message_text(
                MESSAGES['error_file_not_found'],
                call.message.chat.id,
                call.message.message_id
            )
            return

        # בדיקת גודל
        file_size = os.path.getsize(filepath)
        if file_size > MAX_FILE_SIZE:
            cleanup_file(filepath)
            bot.edit_message_text(
                MESSAGES['error_too_large'],
                call.message.chat.id,
                call.message.message_id
            )
            return

        # עדכון סטטוס - מעלה
        bot.edit_message_text(
            MESSAGES['uploading'],
            call.message.chat.id,
            call.message.message_id
        )

        # שליחת הקובץ
        _send_file(bot, call, filepath, audio_only)

        # מחיקת הודעת סטטוס
        bot.delete_message(call.message.chat.id, call.message.message_id)

        # לוג סיום
        duration = time.time() - start_time
        log_action(
            logger, user_id, "DOWNLOAD_COMPLETE",
            f"Duration: {duration:.1f}s, Size: {format_size(file_size)}"
        )

    except PrivateContentError:
        bot.edit_message_text(
            MESSAGES['error_private'],
            call.message.chat.id,
            call.message.message_id
        )
        log_action(logger, user_id, "DOWNLOAD_ERROR", "Private content")

    except Exception as e:
        logger.error(f"שגיאה בהורדה: {e}", exc_info=True)
        error_msg = str(e)[:100] if str(e) else "Unknown error"
        bot.edit_message_text(
            MESSAGES['error_download'].format(error_msg),
            call.message.chat.id,
            call.message.message_id
        )
        log_action(logger, user_id, "DOWNLOAD_ERROR", str(e))

    finally:
        if filepath:
            cleanup_file(filepath)


def _send_file(bot: TeleBot, call: types.CallbackQuery,
               filepath: str, audio_only: bool) -> None:
    file_size = os.path.getsize(filepath)
    chat_id = call.message.chat.id

    with open(filepath, 'rb') as f:
        if audio_only:
            bot.send_audio(
                chat_id,
                f,
                caption=MESSAGES['done_audio']
            )
        else:
            # מעל ~50MB – שולחים כקובץ רגיל
            if file_size > 50 * 1024 * 1024:
                bot.send_document(
                    chat_id,
                    f,
                    caption=MESSAGES['done_video']
                )
            else:
                bot.send_video(
                    chat_id,
                    f,
                    caption=MESSAGES['done_video'],
                    supports_streaming=True
                )
