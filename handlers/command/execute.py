#!/usr/bin/env python3
"""
Обработчики для выполнения команд
"""

from telegram import Update
from telegram.ext import ContextTypes
from services.ssh_client import execute_server_command
from utils.helpers import safe_send_message

async def run_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выполнение произвольной команды"""
    user_id = update.effective_user.id
    
    if len(context.args) < 2:
        from help import get_help_text
        await safe_send_message(update, get_help_text("run_command"))
        return
    
    try:
        server_id = int(context.args[0])
        command = ' '.join(context.args[1:])
        
        success, result = await execute_server_command(server_id, user_id, command)
        
        if success:
            await safe_send_message(update, f"✅ Результат:\n\n{result}")
        else:
            await safe_send_message(update, f"❌ Ошибка: {result}")
    except ValueError:
        await safe_send_message(update, "❌ ID сервера должен быть числом")