#!/usr/bin/env python3
"""
Бот для пользователя 1594692198
Сгенерирован автоматически
"""

import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Обработчики команд
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Я твой бот!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ℹ️ Это твой личный бот!")

# Основная функция
async def main():
    application = ApplicationBuilder().token("7574386856:AAFrpRDfBXwEXbC0JlwdflGqCPuFpos2u1c").build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    logger.info("Бот запущен")
    
    # Бесконечное ожидание
    while True:
        await asyncio.sleep(3600)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
