"""
שירות לקבלת מידע על סרטונים
"""

import os
import logging
from typing import Dict, List, Any, Optional

import yt_dlp

from config import COOKIES_FILE, MAX_QUALITIES

logger = logging.getLogger(__name__)

# Proxy אופציונלי (נדרש ל-YouTube ב-Render)
PROXY_URL = os.getenv('PROXY_URL')


class PrivateContentError(Exception):
    """שגיאה עבור תוכן פרטי שדורש התחברות"""
    pass


def get_video_info(url: str) -> Optional[Dict[str, Any]]:
    """
    קבלת מידע על סרטון מ-URL

    Args:
        url: קישור לסרטון

    Returns:
        מילון עם מידע על הסרטון

    Raises:
        PrivateContentError: אם התוכן פרטי
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }

    # הוספת cookies אם קיים
    if COOKIES_FILE.exists():
        ydl_opts['cookiefile'] = str(COOKIES_FILE)
        logger.info(f"[video_info] משתמש ב-cookies: {COOKIES_FILE}")
    else:
        logger.warning(f"[video_info] קובץ cookies לא נמצא: {COOKIES_FILE}")

    # הוספת proxy אם מוגדר
    if PROXY_URL:
        ydl_opts['proxy'] = PROXY_URL
        logger.info("[video_info] משתמש ב-proxy")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info

    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e).lower()
        if 'private' in error_msg or 'login' in error_msg or 'sign in' in error_msg:
            raise PrivateContentError()
        raise

    except Exception as e:
        logger.error(f"שגיאה בקבלת מידע: {e}")
        raise


def get_available_qualities(info: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    חילוץ איכויות זמינות מהמידע

    Args:
        info: מילון מידע מ-yt-dlp

    Returns:
        רשימת איכויות זמינות
    """
    qualities = []
    seen_heights = set()

    formats = info.get('formats', [])

    # סינון ומיון פורמטים עם וידאו
    video_formats = [
        f for f in formats
        if f.get('vcodec') != 'none' and f.get('height')
    ]
    video_formats.sort(key=lambda x: x.get('height', 0), reverse=True)

    # הוספת איכויות ייחודיות
    for fmt in video_formats:
        height = fmt.get('height')
        if height and height not in seen_heights:
            seen_heights.add(height)
            qualities.append({
                'format_id': fmt.get('format_id'),
                'height': height,
                'label': f"{height}p",
                'filesize': fmt.get('filesize') or fmt.get('filesize_approx'),
                'ext': fmt.get('ext', 'mp4')
            })

    # הוספת אופציית אודיו בלבד
    audio_formats = [
        f for f in formats
        if f.get('vcodec') == 'none' and f.get('acodec') != 'none'
    ]

    if audio_formats:
        best_audio = max(audio_formats, key=lambda x: x.get('abr', 0) or 0)
        qualities.append({
            'format_id': best_audio.get('format_id'),
            'height': 0,
            'label': 'אודיו בלבד 🎵',
            'filesize': best_audio.get('filesize') or best_audio.get('filesize_approx'),
            'ext': best_audio.get('ext', 'mp3'),
            'audio_only': True
        })

    return qualities[:MAX_QUALITIES]


def format_video_details(info: Dict[str, Any]) -> str:
    """
    יצירת טקסט מפורמט עם פרטי הסרטון

    Args:
        info: מילון מידע מ-yt-dlp

    Returns:
        טקסט מפורמט להצגה
    """
    from utils import format_duration, format_number, format_size

    title = info.get('title', 'לא ידוע')[:100]
    duration = format_duration(info.get('duration'))
    uploader = info.get('uploader', info.get('channel', 'לא ידוע'))

    # פורמט תאריך
    upload_date = info.get('upload_date', '')
    if upload_date and len(upload_date) == 8:
        upload_date = f"{upload_date[6:8]}/{upload_date[4:6]}/{upload_date[:4]}"
    else:
        upload_date = "לא ידוע"

    view_count = format_number(info.get('view_count'))
    platform = info.get('extractor', 'לא ידוע').replace(':', ' - ')

    # איכויות זמינות
    qualities = get_available_qualities(info)
    quality_text = ", ".join([
        q['label'] for q in qualities
        if not q.get('audio_only')
    ]) or "לא ידוע"

    # גודל קובץ משוער
    best_format = info.get('filesize') or info.get('filesize_approx')
    if not best_format:
        for fmt in info.get('formats', []):
            if fmt.get('filesize'):
                best_format = fmt['filesize']
                break
    file_size = format_size(best_format)

    return f"""📹 *פרטי הסרטון*

*כותרת:* {title}

⏱️ *משך:* {duration}
👤 *מעלה:* {uploader}
📅 *תאריך העלאה:* {upload_date}
👁️ *צפיות:* {view_count}
🌐 *פלטפורמה:* {platform}

📊 *איכויות זמינות:* {quality_text}
💾 *גודל משוער:* {file_size}"""
