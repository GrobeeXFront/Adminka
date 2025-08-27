#!/usr/bin/env python3
"""
Обработчики для редактирования сервера
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from conversation.states import EDIT_CHOOSE, EDIT_VALUE
from conversation.storage import edit_data
from database import get_server_config, update_user_server
from utils.helpers import safe_send_message

async def edit_server_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало процесса редактирования сервера"""
    user_id = update.effective_user.id
    
    if not context.args:
        await safe_send_message(update, "📝 Использование: /edit_server <id_сервера>")
        return ConversationHandler.END
    
    try:
        server_id = int(context.args[0])
        server_config = get_server_config(server_id, user_id)
        
        if not server_config:
            await safe_send_message(update, "❌ Сервер не найден")
            return ConversationHandler.END
        
        edit_data[user_id] = {'server_id': server_id, 'server_config': server_config}
        
        await safe_send_message(update,
            "✏️ Редактирование сервера\n\n"
            "Выберите поле для редактирования:\n"
            "1. name - Название сервера\n"
            "2. hostname - Hostname/IP\n"
            "3. username - Имя пользователя\n"
            "4. password - Пароль\n"
            "5. port - Порт SSH\n"
            "6. directory - Директория\n"
            "7. filename - Имя файла бота\n\n"
            "Введите номер поля (1-7) или /cancel для отмены:"
        )
        return EDIT_CHOOSE
        
    except ValueError:
        await safe_send_message(update, "❌ ID сервера должен быть числом")
        return ConversationHandler.END

async def edit_server_choose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор поле для редактирования"""
    user_id = update.effective_user.id
    choice = update.message.text.strip()
    
    if choice.lower() == '/cancel':
        await safe_send_message(update, "❌ Редактирование отменено")
        del edit_data[user_id]
        return ConversationHandler.END
    
    field_mapping = {
        '1': 'name', '2': 'hostname', '3': 'username',
        '4': 'password', '5': 'port', '6': 'directory', '7': 'filename'
    }
    
    if choice not in field_mapping:
        await safe_send_message(update, "❌ Неверный выбор. Введите число от 1 до 7:")
        return EDIT_CHOOSE
    
    field = field_mapping[choice]
    edit_data[user_id]['field'] = field
    
    current_value = edit_data[user_id]['server_config'].get(field, '')
    
    if field == 'password':
        current_display = 'скрыт' if current_value else 'не установлен'
    else:
        current_display = current_value or 'не установлен'
    
    await safe_send_message(update,
        f"✏️ Редактирование поле: {field}\n"
        f"Текущее значение: {current_display}\n\n"
        f"Введите новое значение или /cancel для отмены:"
    )
    return EDIT_VALUE

async def edit_server_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нового значения"""
    user_id = update.effective_user.id
    new_value = update.message.text.strip()
    
    if new_value.lower() == '/cancel':
        await safe_send_message(update, "❌ Редактирование отменено")
        del edit_data[user_id]
        return ConversationHandler.END
    
    server_id = edit_data[user_id]['server_id']
    field = edit_data[user_id]['field']
    
    # Специальная обработка для разных полей
    if field == 'port':
        try:
            new_value = int(new_value)
            if new_value < 1 or new_value > 65535:
                raise ValueError
        except ValueError:
            await safe_send_message(update, "❌ Порт должен быть числом от 1 до 65535. Попробуйте снова:")
            return EDIT_VALUE
    
    elif field == 'password':
        if new_value.lower() == 'none':
            new_value = None
        elif new_value == '-':
            new_value = None
    
    # Обновляем сервер
    field_mapping = {
        'name': 'server_name',
        'hostname': 'hostname',
        'username': 'username',
        'password': 'password',
        'port': 'port',
        'directory': 'bot_directory',
        'filename': 'bot_filename'
    }
    
    db_field = field_mapping[field]
    success, message = update_user_server(server_id, user_id, **{db_field: new_value})
    
    await safe_send_message(update, message)
    del edit_data[user_id]
    
    return ConversationHandler.END

async def edit_server_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена редактирования сервера"""
    user_id = update.effective_user.id
    if user_id in edit_data:
        del edit_data[user_id]
    
    await safe_send_message(update, "❌ Редактирование отменено")
    return ConversationHandler.END