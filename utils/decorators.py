#!/usr/bin/env python3
"""
Декораторы для обработчиков
"""

from telegram import Update
from telegram.ext import ContextTypes
from typing import Callable, Any
from database import get_server_config

def require_server_id(func: Callable) -> Callable:
    """Декоратор для проверки server_id"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not context.args:
            await update.message.reply_text("❌ Требуется ID сервера")
            return
        
        try:
            server_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ ID сервера должен быть числом")
            return
        
        return await func(update, context, server_id, *args, **kwargs)
    return wrapper

def require_server_exists(func: Callable) -> Callable:
    """Декоратор для проверки существования сервера"""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, server_id: int, *args, **kwargs):
        user_id = update.effective_user.id
        server_config = get_server_config(server_id, user_id)
        
        if not server_config:
            await update.message.reply_text("❌ Сервер не найден")
            return
        
        return await func(update, context, server_id, server_config, *args, **kwargs)
    return wrapper