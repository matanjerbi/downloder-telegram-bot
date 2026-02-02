"""
הנדלרים לטיפול בהודעות ו-callbacks
"""

from .commands import register_command_handlers
from .url import register_url_handlers
from .callbacks import register_callback_handlers


def register_all_handlers(bot):
    """
    רישום כל ההנדלרים לבוט

    Args:
        bot: אובייקט הבוט
    """
    register_command_handlers(bot)
    register_url_handlers(bot)
    register_callback_handlers(bot)
