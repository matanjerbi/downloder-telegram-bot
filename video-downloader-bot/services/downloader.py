"""
שירות הורדת סרטונים
"""

import os
import time
import logging
from typing import Optional
from pathlib import Path

import yt_dlp

from config import DOWNLOADS_DIR, COOKIES_FILE

logger = logging.getLogger(__name__)

# Proxy אופציונלי (נדרש ל-YouTube ב-Render)
PROXY_URL = os.getenv('PROXY_URL')  # לדוגמה: socks5://user:pass@proxy.example.com:1080


def download_video(url: str, quality: str = 'best', audio_only: bool = False) -> Optional[str]:
    """
    הורדת סרטון מ-URL

    Args:
        url: קישור לסרטון
        quality: איכות רצויה (best/720/480 וכו')
        audio_only: האם להוריד רק אודיו

    Returns:
        נתיב הקובץ שהורד, או None אם נכשל
    """
    timestamp = int(time.time())
    output_template = str(DOWNLOADS_DIR / f'%(title).50s_{timestamp}.%(ext)s')

    ydl_opts = {
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 150,
    }

    # הוספת cookies אם קיים
    if COOKIES_FILE.exists():
        ydl_opts['cookiefile'] = str(COOKIES_FILE)
        logger.info(f"משתמש ב-cookies: {COOKIES_FILE}")
    else:
        logger.warning(f"קובץ cookies לא נמצא: {COOKIES_FILE}")

    # הוספת proxy אם מוגדר (נדרש ל-YouTube ב-Render)
    if PROXY_URL:
        ydl_opts['proxy'] = PROXY_URL
        logger.info("משתמש ב-proxy")

    # הגדרת פורמט לפי סוג ההורדה
    if audio_only:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        if quality == 'best':
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        else:
            ydl_opts['format'] = (
                f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/'
                f'best[height<={quality}][ext=mp4]/best'
            )
        ydl_opts['merge_output_format'] = 'mp4'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            # התאמת סיומת הקובץ
            if audio_only:
                base = os.path.splitext(filename)[0]
                filename = base + '.mp3'
            else:
                if not filename.endswith('.mp4'):
                    base = os.path.splitext(filename)[0]
                    if os.path.exists(base + '.mp4'):
                        filename = base + '.mp4'

            # בדיקה אם הקובץ קיים
            if os.path.exists(filename):
                return filename

            # חיפוש הקובץ בתיקייה לפי timestamp
            return _find_downloaded_file(timestamp)

    except Exception as e:
        logger.error(f"שגיאה בהורדה: {e}")
        raise


def _find_downloaded_file(timestamp: int) -> Optional[str]:
    """
    חיפוש קובץ שהורד לפי timestamp

    Args:
        timestamp: חותמת זמן שהוספה לשם הקובץ

    Returns:
        נתיב הקובץ אם נמצא
    """
    for file in DOWNLOADS_DIR.iterdir():
        if str(timestamp) in file.name:
            return str(file)
    return None
