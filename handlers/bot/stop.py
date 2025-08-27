#!/usr/bin/env python3
"""
Обработчики для остановки бота
"""

import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from database import get_server_config
from services.ssh_client import execute_server_command
from utils.helpers import safe_send_message

async def stop_bot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Остановка бота на сервера"""
    user_id = update.effective_user.id
    
    if not context.args:
        from help import get_help_text
        await safe_send_message(update, get_help_text("stop_bot"))
        return
    
    try:
        server_id = int(context.args[0])
        service_name = context.args[1] if len(context.args) > 1 else "bot"
        
        # Получаем конфигурацию сервера
        server_config = get_server_config(server_id, user_id)
        if not server_config:
            await safe_send_message(update, "❌ Сервер не найден")
            return
        
        bot_filename = server_config.get('bot_filename', 'bot.py')
        
        # Сначала проверяем, запущен ли бот
        check_command = f"pgrep -f 'python3.*{bot_filename}'"
        check_success, check_result = await execute_server_command(server_id, user_id, check_command)
        
        if not check_success or not check_result.strip():
            await safe_send_message(update, "✅ Бот уже остановлен")
            return
        
        # Пробуем остановить через systemd
        systemd_command = f"systemctl stop {service_name}"
        systemd_success, systemd_result = await execute_server_command(server_id, user_id, systemd_command)
        
        if systemd_success:
            await safe_send_message(update, f"✅ Бот остановлен через systemd сервис: {service_name}")
            return
        
        # Если systemd не сработал, останавливаем процессы
        pids = check_result.strip().split('\n')
        stop_command = f"kill {' '.join(pids)}"
        stop_success, stop_result = await execute_server_command(server_id, user_id, stop_command)
        
        if stop_success:
            # Проверяем остановились ли процессы
            await asyncio.sleep(2)
            check_success, check_result = await execute_server_command(server_id, user_id, check_command)
            
            if not check_success or not check_result.strip():
                await safe_send_message(update, f"✅ Бот остановлен\nЗавершено процессов: {len(pids)}")
            else:
                # Принудительная остановка
                force_command = f"kill -9 {' '.join(pids)}"
                force_success, force_result = await execute_server_command(server_id, user_id, force_command)
                
                if force_success:
                    await safe_send_message(update, "✅ Бот принудительно остановлен")
                else:
                    await safe_send_message(update, f"⚠️ Не удалось остановить все процессы: {check_result}")
        else:
            await safe_send_message(update, f"❌ Ошибка остановки: {stop_result}")
            
    except ValueError:
        await safe_send_message(update, "❌ ID сервера должен быть числом")