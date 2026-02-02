"""
הנדלרים לפקודות /start ו-/help
"""

import logging
from telebot import TeleBot, types

from config import MESSAGES
from utils.helpers import log_action

logger = logging.getLogger(__name__)


def register_command_handlers(bot: TeleBot) -> None:
    """
    רישום הנדלרים לפקודות

    Args:
        bot: אובייקט הבוט
    """

    @bot.message_handler(commands=['start'])
    def handle_start(message: types.Message) -> None:
        """טיפול בפקודת /start"""
        log_action(logger, message.from_user.id, "START", "")
        bot.send_message(
            message.chat.id,
            MESSAGES['welcome'],
            parse_mode='Markdown'
        )

    @bot.message_handler(commands=['help'])
    def handle_help(message: types.Message) -> None:
        """טיפול בפקודת /help"""
        log_action(logger, message.from_user.id, "HELP", "")
        bot.send_message(
            message.chat.id,
            MESSAGES['help'],
            parse_mode='Markdown',
            disable_web_page_preview=True
        )
