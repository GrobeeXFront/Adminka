#!/usr/bin/env python3
"""
Главный файл SSH админ-бота
"""

import asyncio
import fcntl
import sys

from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters

# Импортируем конфигурацию
try:
    from config import BOT_TOKEN, LOCK_FILE, POLL_INTERVAL
    from utils.logging import setup_logging
    from handlers import (
        start_handler, my_servers_handler,
        server_status_handler, start_bot_handler, stop_bot_handler,
        bot_logs_handler, run_command_handler, delete_server_handler, help_handler,
        add_server_start, add_server_name, add_server_hostname, add_server_username,
        add_server_password, add_server_port, add_server_directory, add_server_filename, add_server_cancel,
        edit_server_start, edit_server_choose, edit_server_value, edit_server_cancel
    )
    # ИСПРАВЛЕНО: импорт состояний из states.py, а не storage.py
    from conversation.states import NAME, HOSTNAME, USERNAME, PASSWORD, PORT, DIRECTORY, FILENAME, EDIT_CHOOSE, EDIT_VALUE
    from database import init_database
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    sys.exit(1)

logger = setup_logging()

def acquire_lock():
    """Получение блокировки для предотвращения множественных запусков"""
    try:
        lock_file = open(LOCK_FILE, 'w')
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        logger.info("Блокировка успешно получена")
        return lock_file
    except IOError:
        logger.error("Другой экземпляр бота уже запущен")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Ошибка получения блокировки: {e}")
        sys.exit(1)

async def error_handler(update, context):
    """Обработчик ошибок"""
    logger.error(f"Ошибка при обработке обновления: {context.error}", exc_info=True)

async def main():
    """Основная функция запуска бота"""
    lock_file = acquire_lock()
    
    try:
        # Инициализация базы данных
        init_database()
        
        application = ApplicationBuilder()\
            .token(BOT_TOKEN)\
            .concurrent_updates(True)\
            .build()
        
        # ConversationHandler для добавления сервера
        add_server_conv_handler = ConversationHandler(
            entry_points=[CommandHandler('add_server', add_server_start)],
            states={
                NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_server_name)],
                HOSTNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_server_hostname)],
                USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_server_username)],
                PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_server_password)],
                PORT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_server_port)],
                DIRECTORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_server_directory)],
                FILENAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_server_filename)],
            },
            fallbacks=[CommandHandler('cancel', add_server_cancel)],
        )
        
        # ConversationHandler для редактирования сервера
        edit_server_conv_handler = ConversationHandler(
            entry_points=[CommandHandler('edit_server', edit_server_start)],
            states={
                EDIT_CHOOSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_server_choose)],
                EDIT_VALUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_server_value)],
            },
            fallbacks=[CommandHandler('cancel', edit_server_cancel)],
        )
        
        # Регистрация обработчиков команд
        handlers = [
            add_server_conv_handler,
            edit_server_conv_handler,
            CommandHandler("start", start_handler),
            CommandHandler("my_servers", my_servers_handler),
            CommandHandler("server_status", server_status_handler),
            CommandHandler("start_bot", start_bot_handler),
            CommandHandler("stop_bot", stop_bot_handler),
            CommandHandler("bot_logs", bot_logs_handler),
            CommandHandler("run_command", run_command_handler),
            CommandHandler("delete_server", delete_server_handler),
            CommandHandler("help", help_handler),
        ]
        
        for handler in handlers:
            application.add_handler(handler)
        
        application.add_error_handler(error_handler)
        
        logger.info("Запуск SSH админ-бота...")
        await application.initialize()
        await application.start()
        await application.updater.start_polling(
            drop_pending_updates=True,
            timeout=30,
            poll_interval=POLL_INTERVAL
        )
        
        logger.info("Админ-бот успешно запущен и готов к работе")
        
        while True:
            await asyncio.sleep(3600)
            
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        raise
    finally:
        logger.info("Завершение работы админ-бота...")
        if 'application' in locals():
            await application.updater.stop()
            await application.stop()
            await application.shutdown()
        try:
            fcntl.flock(lock_file, fcntl.LOCK_UN)
            lock_file.close()
            logger.info("Блокировка освобождена")
        except Exception as e:
            logger.error(f"Ошибка при освобождении блокировки: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Остановлено по Ctrl+C")
    except Exception as e:
        logger.error(f"Фатальная ошибка: {e}", exc_info=True)
    finally:
        logger.info("Работа админ-бота завершена")