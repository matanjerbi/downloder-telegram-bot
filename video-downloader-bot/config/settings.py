"""
הגדרות וקבועים
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# טעינת משתני סביבה
load_dotenv()

# נתיבים
BASE_DIR = Path(__file__).parent.parent
DOWNLOADS_DIR = BASE_DIR / 'downloads'
COOKIES_FILE = BASE_DIR / 'cookies.txt'

# טוקן הבוט
BOT_TOKEN = os.getenv('BOT_TOKEN')

# מגבלות
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB - מגבלת טלגרם
DOWNLOAD_TIMEOUT = 600  # 10 דקות
MAX_QUALITIES = 6  # מספר מקסימלי של אופציות איכות

# יצירת תיקיות נדרשות
DOWNLOADS_DIR.mkdir(exist_ok=True)
