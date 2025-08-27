#!/usr/bin/env python3
"""
Обработчики для запуска бота
"""

import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from database import get_server_config
from services.ssh_client import execute_server_command
from utils.helpers import safe_send_message

async def start_bot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запуск бота на сервере"""
    user_id = update.effective_user.id
    
    if not context.args:
        from help import get_help_text
        await safe_send_message(update, get_help_text("start_bot"))
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
        bot_directory = server_config.get('bot_directory', '/home')
        
        # Проверяем есть ли systemd сервис
        if server_config.get('service_name'):
            service_name = server_config['service_name']
            # Проверяем существует ли сервис
            from services.systemd_manager import check_systemd_service, manage_systemd_service
            service_exists, _ = await check_systemd_service(server_id, user_id, service_name)
            
            if service_exists:
                # Запускаем через systemd
                success, result = await manage_systemd_service(server_id, user_id, service_name, 'start')
                if success:
                    await safe_send_message(update, f"✅ Бот запущен через systemd: {service_name}")
                    return
        
        # Сначала проверяем, не запущен ли уже бот (игнорируем ошибки подключения)
        check_command = f"pgrep -f 'python3.*{bot_filename}'"
        check_success, check_result = await execute_server_command(server_id, user_id, check_command)
        
        # Если есть процессы, значит бот уже запущен
        if check_success and check_result.strip():
            pids = check_result.strip().split('\n')
            await safe_send_message(update, f"⚠️ Бот уже запущен\nPID процессов: {', '.join(pids)}")
            return
        
        # Пробуем запустить через systemd (игнорируем ошибки выполнения)
        systemd_command = f"systemctl start {service_name}"
        systemd_success, systemd_result = await execute_server_command(server_id, user_id, systemd_command)
        
        # Даем время на запуск в любом случае
        await asyncio.sleep(3)
        
        # Проверяем, запустился ли бот (основная проверка)
        check_success, check_result = await execute_server_command(server_id, user_id, check_command)
        
        if check_success and check_result.strip():
            pids = check_result.strip().split('\n')
            # Бот запущен успешно, независимо от ошибок выполнения команд
            if systemd_success:
                await safe_send_message(update, f"✅ Бот запущен через systemd сервис: {service_name}\nPID: {', '.join(pids)}")
            else:
                await safe_send_message(update, f"✅ Бот запущен (systemd не сработал, но бот работает)\nPID: {', '.join(pids)}")
            return
        
        # Если systemd не сработал и бот не запущен, пробуем screen
        screen_command = f"cd {bot_directory} && screen -dmS bot_{bot_filename} python3 {bot_filename}"
        screen_success, screen_result = await execute_server_command(server_id, user_id, screen_command)
        
        # Даем время на запуск
        await asyncio.sleep(3)
        
        # Снова проверяем статус
        check_success, check_result = await execute_server_command(server_id, user_id, check_command)
        
        if check_success and check_result.strip():
            pids = check_result.strip().split('\n')
            await safe_send_message(update, f"✅ Бот запущен через screen\nPID: {', '.join(pids)}")
            return
        
        # Пробуем nohup
        nohup_command = f"cd {bot_directory} && nohup python3 {bot_filename} > {bot_filename.replace('.py', '.log')} 2>&1 &"
        nohup_success, nohup_result = await execute_server_command(server_id, user_id, nohup_command)
        
        await asyncio.sleep(3)
        check_success, check_result = await execute_server_command(server_id, user_id, check_command)
        
        if check_success and check_result.strip():
            pids = check_result.strip().split('\n')
            await safe_send_message(update, f"✅ Бот запущен через nohup\nPID: {', '.join(pids)}")
            return
        
        # Пробуем простой запуск
        direct_command = f"cd {bot_directory} && python3 {bot_filename} &"
        direct_success, direct_result = await execute_server_command(server_id, user_id, direct_command)
        
        await asyncio.sleep(3)
        check_success, check_result = await execute_server_command(server_id, user_id, check_command)
        
        if check_success and check_result.strip():
            pids = check_result.strip().split('\n')
            await safe_send_message(update, f"✅ Бот запущен напрямую\nPID: {', '.join(pids)}")
            return
        
        # Финальная проверка - возможно бот все-таки запустился
        final_check_success, final_check_result = await execute_server_command(server_id, user_id, check_command)
        
        if final_check_success and final_check_result.strip():
            pids = final_check_result.strip().split('\n')
            await safe_send_message(update, f"✅ Бот запущен (несмотря на ошибки выполнения команд)\nPID: {', '.join(pids)}")
        else:
            # Проверяем логи на наличие информации о запуске
            log_check = f"cd {bot_directory} && tail -20 {bot_filename.replace('.py', '.log')} 2>/dev/null || echo 'Лог файл не найден или пуст'"
            log_success, log_result = await execute_server_command(server_id, user_id, log_check)
            
            await safe_send_message(update,
                f"❌ Не удалось подтвердить запуск бота\n"
                f"Проверьте:\n"
                f"1. Существует ли файл: {bot_directory}/{bot_filename}\n"
                f"2. Права на выполнение файла\n"
                f"3. Логи: {log_result if log_success else 'Не удалось прочитать логи'}"
            )
            
    except ValueError:
        await safe_send_message(update, "❌ ID сервера должен быть числом")
    except Exception as e:
        await safe_send_message(update, f"❌ Непредвиденная ошибка при запуске: {str(e)}")