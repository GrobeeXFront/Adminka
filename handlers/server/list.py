#!/usr/bin/env python3
"""
Обработчики для списка серверов
"""

from telegram import Update
from telegram.ext import ContextTypes
from database import get_user_servers
from utils.helpers import safe_send_message

async def my_servers_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список серверов пользователя"""
    user_id = update.effective_user.id
    servers = get_user_servers(user_id)
    
    if not servers:
        await safe_send_message(update, 
            "🤷 У вас пока нет добавленных серверов.\n"
            "Используйте /add_server для добавления первого сервера"
        )
        return
    
    response = "📋 Ваши серверы:\n\n"
    for server in servers:
        response += f"🖥️ {server['name']} (ID: {server['id']})\n"
        response += f"   🌐 {server['hostname']}:{server['port']}\n"
        response += f"   👤 {server['username']}\n"
        response += f"   📁 {server['directory']}\n"
        response += f"   📄 {server['filename']}\n\n"
    
    await safe_send_message(update, response)