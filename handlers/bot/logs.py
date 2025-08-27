#!/usr/bin/env python3
"""
Обработчики для логов бота
"""

from telegram import Update
from telegram.ext import ContextTypes
from database import get_server_config
from services.ssh_client import execute_server_command
from utils.helpers import safe_send_message

async def bot_logs_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Логи бота на сервере"""
    user_id = update.effective_user.id
    
    if not context.args:
        from help import get_help_text
        await safe_send_message(update, get_help_text("bot_logs"))
        return
    
    try:
        server_id = int(context.args[0])
        
        # Получаем конфигурацию сервера
        server_config = get_server_config(server_id, user_id)
        if not server_config:
            await safe_send_message(update, "❌ Сервер не найден")
            return
        
        bot_filename = server_config.get('bot_filename', 'bot.py')
        log_file = context.args[1] if len(context.args) > 1 else f"{bot_filename.replace('.py', '.log')}"
        
        from config import MAX_LOG_LINES
        command = f"cd {server_config['bot_directory']} && tail -n {MAX_LOG_LINES} {log_file}"
        success, result = await execute_server_command(server_id, user_id, command)
        
        if success:
            await safe_send_message(update, f"📋 Логи бота:\n\n{result}")
        else:
            await safe_send_message(update, f"❌ Ошибка: {result}")
    except ValueError:
        await safe_send_message(update, "❌ ID сервера должен быть числом")