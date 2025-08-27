#!/usr/bin/env python3
"""
Вспомогательные функции
"""

from telegram import Update
from typing import Optional

async def safe_send_message(update: Update, text: str, max_length: int = 4096) -> None:
    """Безопасная отправка сообщений с учетом ограничения длины"""
    if len(text) > max_length:
        text = text[:max_length - 100] + "\n\n... (сообщение обрезано)"
    
    try:
        if update and update.message:
            await update.message.reply_text(text)
        elif update and update.effective_chat:
            await update.effective_chat.send_message(text)
    except Exception:
        pass