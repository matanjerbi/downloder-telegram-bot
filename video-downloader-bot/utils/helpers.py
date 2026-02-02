"""
פונקציות עזר כלליות
"""

import os
import re
import logging
import shutil
from typing import Optional


def setup_logger(name: str) -> logging.Logger:
    """
    הגדרת לוגר עם פורמט אחיד

    Args:
        name: שם הלוגר

    Returns:
        אובייקט Logger מוגדר
    """
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] [%(message)s]',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(name)


def extract_url(text: str) -> Optional[str]:
    """
    חילוץ URL מטקסט

    Args:
        text: טקסט שעשוי להכיל URL

    Returns:
        URL אם נמצא, אחרת None
    """
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    match = re.search(url_pattern, text)
    return match.group(0) if match else None


def cleanup_file(filepath: str) -> None:
    """
    מחיקת קובץ זמני

    Args:
        filepath: נתיב הקובץ למחיקה
    """
    logger = logging.getLogger(__name__)
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"נמחק קובץ: {filepath}")
    except Exception as e:
        logger.error(f"שגיאה במחיקת קובץ: {e}")


def check_ffmpeg() -> bool:
    """
    בדיקה אם ffmpeg מותקן במערכת

    Returns:
        True אם מותקן, False אחרת
    """
    return shutil.which('ffmpeg') is not None


def log_action(logger: logging.Logger, user_id: int, action: str, details: str = "") -> None:
    """
    רישום פעולת משתמש ללוג

    Args:
        logger: אובייקט הלוגר
        user_id: מזהה המשתמש
        action: סוג הפעולה
        details: פרטים נוספים
    """
    logger.info(f"[USER:{user_id}] [{action}] {details}")
