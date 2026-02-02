"""
פונקציות פורמט להצגת נתונים
"""

from typing import Optional


def format_duration(seconds: Optional[int]) -> str:
    """
    המרת שניות לפורמט MM:SS או HH:MM:SS

    Args:
        seconds: מספר שניות

    Returns:
        מחרוזת בפורמט זמן קריא
    """
    if not seconds:
        return "לא ידוע"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def format_number(num: Optional[int]) -> str:
    """
    פורמט מספרים עם פסיקים

    Args:
        num: מספר לפורמט

    Returns:
        מחרוזת עם פסיקים (1,234,567)
    """
    if not num:
        return "לא ידוע"
    return f"{num:,}"


def format_size(bytes_size: Optional[int]) -> str:
    """
    המרת בייטים לפורמט קריא (KB, MB, GB)

    Args:
        bytes_size: גודל בבייטים

    Returns:
        מחרוזת עם יחידה מתאימה
    """
    if not bytes_size:
        return "לא ידוע"

    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"
