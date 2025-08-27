#!/usr/bin/env python3
"""
Базовые обработчики команд
"""

from telegram import Update
from telegram.ext import ContextTypes
from help import get_help_text
from utils.helpers import safe_send_message

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await safe_send_message(update, get_help_text("start"))

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь"""
    if context.args:
        command = context.args[0]
        help_text = get_help_text(command)
    else:
        help_text = get_help_text()
    
    await safe_send_message(update, help_text)