#!/usr/bin/env python3
"""
Обработчики для удаления сервера
"""

from telegram import Update
from telegram.ext import ContextTypes
from database import delete_user_server
from utils.helpers import safe_send_message

async def delete_server_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаление сервера"""
    user_id = update.effective_user.id
    
    if not context.args:
        await safe_send_message(update, "📝 Использование: /delete_server <id_сервера>")
        return
    
    try:
        server_id = int(context.args[0])
        success, message = delete_user_server(server_id, user_id)
        await safe_send_message(update, message)
    except ValueError:
        await safe_send_message(update, "❌ ID сервера должен быть числом")