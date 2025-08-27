#!/usr/bin/env python3
"""
Обработчики для статуса сервера
"""

from telegram import Update
from telegram.ext import ContextTypes
from database import get_server_config
from services.ssh_client import execute_server_command
from services.bot_checker import check_bot_status
from utils.helpers import safe_send_message

async def server_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статус сервера"""
    user_id = update.effective_user.id
    
    if not context.args:
        from help import get_help_text
        await safe_send_message(update, get_help_text("server_status"))
        return
    
    try:
        server_id = int(context.args[0])
        
        # Получаем информацию о сервере
        server_config = get_server_config(server_id, user_id)
        if not server_config:
            await safe_send_message(update, "❌ Сервер не найден")
            return
        
        # Выполняем команды для получения статуса
        commands = {
            "uptime": "uptime",
            "memory": "free -h | awk '/^Mem:/ {print $3\"/\"$2}'",
            "disk": "df -h / | awk 'NR==2 {print $4\" свободно из \"$2}'",
            "load": "cat /proc/loadavg | awk '{print $1\", \"$2\", \"$3}'"
        }
        
        results = {}
        for key, cmd in commands.items():
            success, result = await execute_server_command(server_id, user_id, cmd)
            results[key] = result if success else "❌ Ошибка"
        
        # Проверяем статус бота
        bot_filename = server_config.get('bot_filename', 'bot.py')
        bot_status = await check_bot_status(server_id, user_id, bot_filename)
        
        # Форматируем красивый вывод
        status_message = (
            f"📊 Статус сервера: {server_config['name']}\n"
            f"🌐 {server_config['hostname']}:{server_config['port']}\n\n"
            f"🤖 Статус бота: {bot_status}\n\n"
            f"⏰ Время работы: {results.get('uptime', 'N/A')}\n"
            f"💾 Память: {results.get('memory', 'N/A')}\n"
            f"💿 Диск: {results.get('disk', 'N/A')}\n"
            f"📈 Нагрузка: {results.get('load', 'N/A')}\n\n"
            f"👤 Пользователь: {server_config['username']}\n"
            f"📁 Директория: {server_config.get('bot_directory', '/home')}\n"
            f"📄 Файл бота: {bot_filename}"
        )
        
        await safe_send_message(update, status_message)
        
    except ValueError:
        await safe_send_message(update, "❌ ID сервера должен быть числом")