# 🎬 בוט טלגרם להורדת סרטונים

בוט טלגרם פשוט ויעיל להורדת סרטונים מכל פלטפורמה - YouTube, TikTok, Instagram, Twitter ועוד מאות אתרים!

## ✨ תכונות

- 📥 הורדת סרטונים מ-1000+ אתרים
- 🎚️ בחירת איכות (1080p, 720p, 480p...)
- 🎵 אפשרות להורדת אודיו בלבד
- 📊 הצגת פרטי סרטון (משך, צפיות, תאריך...)
- 🔗 זיהוי אוטומטי של קישורים
- 🌐 ממשק בעברית

## 📋 דרישות מקדימות

- Python 3.8 ומעלה
- ffmpeg (להמרת פורמטים)
- טוקן בוט מ-BotFather

## 🚀 התקנה

### 1. שכפול הפרויקט

```bash
cd video-downloader-bot
```

### 2. יצירת סביבה וירטואלית (מומלץ)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# או
.\venv\Scripts\activate  # Windows
```

### 3. התקנת תלויות

```bash
pip install -r requirements.txt
```

### 4. התקנת ffmpeg

**Mac:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**Windows:**
הורד מ-https://ffmpeg.org/download.html והוסף ל-PATH

### 5. יצירת קובץ הגדרות

```bash
cp .env.example .env
```

ערוך את `.env` והוסף את הטוקן:
```
BOT_TOKEN=your_bot_token_here
```

### 6. קבלת טוקן מ-BotFather

1. פתח את @BotFather בטלגרם
2. שלח `/newbot`
3. בחר שם לבוט (למשל: "Video Downloader Bot")
4. בחר username (חייב להסתיים ב-bot, למשל: my_video_dl_bot)
5. העתק את הטוקן ששלח לך BotFather

### 7. הפעלת הבוט

```bash
python bot.py
```

## 📖 שימוש

1. פתח את הבוט בטלגרם
2. שלח קישור לסרטון (מכל פלטפורמה נתמכת)
3. בחר "📊 פרטים" לראות מידע על הסרטון
4. בחר "📥 הורדה" ובחר איכות
5. קבל את הקובץ!

## 🌐 פלטפורמות נתמכות

הבוט משתמש ב-yt-dlp ותומך ביותר מ-1000 אתרים, ביניהם:

- YouTube
- TikTok
- Instagram (פוסטים ציבוריים)
- Twitter/X
- Facebook (סרטונים ציבוריים)
- Reddit
- Vimeo
- Dailymotion
- Twitch (קליפים)
- SoundCloud
- ועוד רבים...

📋 רשימה מלאה: https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md

## 🔐 תוכן פרטי (אופציונלי)

אם אתה צריך לגשת לתוכן שדורש התחברות:

1. התקן תוסף דפדפן לייצוא cookies (למשל "Get cookies.txt")
2. היכנס לאתר הרלוונטי
3. ייצא את ה-cookies לקובץ `cookies.txt`
4. שים את הקובץ בתיקיית הפרויקט

⚠️ **שים לב:** רוב האתרים עובדים בלי התחברות!

## ⚠️ מגבלות

- גודל קובץ מקסימלי: 2GB (מגבלת טלגרם)
- זמן הורדה מקסימלי: 10 דקות
- תוכן פרטי דורש cookies

## 🔧 פתרון בעיות

### הבוט לא מגיב
- ודא שהטוקן נכון ב-.env
- בדוק שיש חיבור לאינטרנט

### שגיאה בהורדה
- ודא ש-ffmpeg מותקן: `ffmpeg -version`
- נסה קישור אחר
- בדוק שהתוכן לא פרטי

### הקובץ לא נשלח
- ייתכן שהקובץ גדול מ-2GB
- נסה איכות נמוכה יותר

### "התוכן פרטי ודורש התחברות"
- הוסף קובץ cookies.txt (ראה הוראות למעלה)
- או נסה קישור לתוכן ציבורי

## 📝 רישיון

MIT License

## 🤝 תרומה

נשמח לקבל Pull Requests!
