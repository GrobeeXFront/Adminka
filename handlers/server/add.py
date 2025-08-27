#!/usr/bin/env python3
"""
Обработчики для добавления сервера
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from conversation.states import NAME, HOSTNAME, USERNAME, PASSWORD, PORT, DIRECTORY, FILENAME, SERVICE_NAME, SERVICE_CONFIRM
from conversation.storage import server_data
from database import add_user_server
from utils.helpers import safe_send_message

async def add_server_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало процесса добавления сервера"""
    user_id = update.effective_user.id
    server_data[user_id] = {}
    
    await safe_send_message(update, 
        "🆕 Добавление нового сервера\n\n"
        "Шаг 1/7: Введите название сервера (произвольное имя):"
    )
    return NAME

async def add_server_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка названия сервера"""
    user_id = update.effective_user.id
    server_name = update.message.text.strip()
    
    if len(server_name) < 2:
        await safe_send_message(update, "❌ Название сервера должно быть не менее 2 символов. Попробуйте снова:")
        return NAME
    
    server_data[user_id]['name'] = server_name
    
    await safe_send_message(update,
        "Шаг 2/7: Введите hostname или IP адрес сервера:\n"
        "Пример: example.com или 192.168.1.100"
    )
    return HOSTNAME

async def add_server_hostname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка hostname сервера"""
    user_id = update.effective_user.id
    hostname = update.message.text.strip()
    
    if not hostname:
        await safe_send_message(update, "❌ Hostname не может быть пустым. Попробуйте снова:")
        return HOSTNAME
    
    server_data[user_id]['hostname'] = hostname
    
    await safe_send_message(update,
        "Шаг 3/7: Введите имя пользователя для SSH подключения:\n"
        "Пример: root, user, admin"
    )
    return USERNAME

async def add_server_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка username сервера"""
    user_id = update.effective_user.id
    username = update.message.text.strip()
    
    if not username:
        await safe_send_message(update, "❌ Имя пользователя не может быть пустым. Попробуйте снова:")
        return USERNAME
    
    server_data[user_id]['username'] = username
    
    await safe_send_message(update,
        "Шаг 4/7: Введите пароль пользователя:\n"
        "• Если используете SSH ключ, введите: -\n"
        "• Если пароль пустой, введите: none\n"
        "• Для отменя введите: /cancel"
    )
    return PASSWORD

async def add_server_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка пароля сервера"""
    user_id = update.effective_user.id
    password = update.message.text.strip()
    
    if password.lower() == '/cancel':
        await safe_send_message(update, "❌ Добавление сервера отменено")
        del server_data[user_id]
        return ConversationHandler.END
    
    if password.lower() == 'none':
        password = None
    elif password == '-':
        password = None
    
    server_data[user_id]['password'] = password
    
    await safe_send_message(update,
        "Шаг 5/7: Введите порт SSH (по умолчанию 22):\n"
        "• Для использования порта по умолчанию введите: 22\n"
        "• Для отмены введите: /cancel"
    )
    return PORT

async def add_server_port(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка порта сервера"""
    user_id = update.effective_user.id
    port_text = update.message.text.strip()
    
    if port_text.lower() == '/cancel':
        await safe_send_message(update, "❌ Добавление сервера отменено")
        del server_data[user_id]
        return ConversationHandler.END
    
    try:
        port = int(port_text)
        if port < 1 or port > 65535:
            raise ValueError
    except ValueError:
        await safe_send_message(update, "❌ Порт должен быть числом от 1 до 65535. Попробуйте снова:")
        return PORT
    
    server_data[user_id]['port'] = port
    
    await safe_send_message(update,
        "Шаг 6/7: Введите рабочую директорию бота:\n"
        "Пример: /home/user/bot или /opt/bot\n"
        "• По умолчанию: /home\n"
        "• Для отмены введите: /cancel"
    )
    return DIRECTORY

async def add_server_directory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка директории сервера"""
    user_id = update.effective_user.id
    directory = update.message.text.strip()
    
    if directory.lower() == '/cancel':
        await safe_send_message(update, "❌ Добавление сервера отменено")
        del server_data[user_id]
        return ConversationHandler.END
    
    if not directory:
        directory = "/home"
    
    server_data[user_id]['directory'] = directory
    
    await safe_send_message(update,
        "Шаг 7/7: Введите имя файла бота:\n"
        "Пример: bot.py, mybot.py, kandrytaxi.py\n"
        "• По умолчанию: bot.py\n"
        "• Для отмены введите: /cancel"
    )
    return FILENAME

async def add_server_filename(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка имени файла бота"""
    user_id = update.effective_user.id
    filename = update.message.text.strip()
    
    if filename.lower() == '/cancel':
        await safe_send_message(update, "❌ Добавление сервера отменено")
        del server_data[user_id]
        return ConversationHandler.END
    
    if not filename:
        filename = "bot.py"
    
    server_data[user_id]['filename'] = filename
    
    await safe_send_message(update,
        "Шаг 8/9: Введите имя systemd сервиса (опционально):\n"
        "• Пример: mybot, telegram-bot, candyshop\n"
        "• Если не используете systemd, введите: -\n"
        "• Для отмены введите: /cancel"
    )
    return SERVICE_NAME

async def add_server_service_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка имени systemd сервиса"""
    user_id = update.effective_user.id
    service_name = update.message.text.strip()
    
    if service_name.lower() == '/cancel':
        await safe_send_message(update, "❌ Добавление сервера отменено")
        del server_data[user_id]
        return ConversationHandler.END
    
    if service_name == '-':
        service_name = None
    
    server_data[user_id]['service_name'] = service_name
    
    # Если указан service_name, предлагаем создать сервис
    if service_name:
        await safe_send_message(update,
            f"🛠️ Хотите создать systemd сервис '{service_name}'?\n"
            f"Это позволит удобно управлять ботом через systemctl\n\n"
            f"Введите 'да' для создания или 'нет' чтобы пропустить:"
        )
        return SERVICE_CONFIRM
    else:
        # Пропускаем создание сервиса
        return await add_server_finish(update, context)

async def add_server_service_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение создания systemd сервиса"""
    user_id = update.effective_user.id
    choice = update.message.text.strip().lower()
    
    if choice == '/cancel':
        await safe_send_message(update, "❌ Добавление сервера отменено")
        del server_data[user_id]
        return ConversationHandler.END
    
    if choice in ['да', 'yes', 'y', 'д']:
        server_data[user_id]['create_service'] = True
    else:
        server_data[user_id]['create_service'] = False
    
    return await add_server_finish(update, context)

async def add_server_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Завершение добавления сервера"""
    user_id = update.effective_user.id
    data = server_data[user_id]
    
    # Добавляем сервер в базу
    success, message = add_user_server(
        user_id=user_id,
        server_name=data['name'],
        hostname=data['hostname'],
        username=data['username'],
        password=data.get('password'),
        port=data.get('port', 22),
        bot_directory=data['directory'],
        bot_filename=data['filename'],
        service_name=data.get('service_name')
    )
    
    # Если нужно создать сервис
    if data.get('create_service') and data.get('service_name'):
        try:
            from services.systemd_manager import create_systemd_service
            service_success, service_message = await create_systemd_service(
                user_id, user_id, data['service_name'], 
                data['directory'], data['filename'], data['username']
            )
            message += f"\n{service_message}"
        except Exception as e:
            message += f"\n⚠️ Ошибка создания сервиса: {str(e)}"
    
    # Вывод сводки
    summary = (
        "📋 Сводка добавленного сервера:\n\n"
        f"🏷️ Название: {data['name']}\n"
        f"🌐 Hostname: {data['hostname']}\n"
        f"👤 Пользователь: {data['username']}\n"
        f"🔐 Пароль: {'используется' if data.get('password') else 'SSH ключ/нет'}\n"
        f"🚪 Порт: {data.get('port', 22)}\n"
        f"📁 Директория: {data['directory']}\n"
        f"📄 Файл бота: {data['filename']}\n"
        f"🛠️ Systemd сервис: {data.get('service_name', 'не используется')}\n\n"
        f"{message}"
    )
    
    await safe_send_message(update, summary)
    del server_data[user_id]
    return ConversationHandler.END

async def add_server_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена добавления сервера"""
    user_id = update.effective_user.id
    if user_id in server_data:
        del server_data[user_id]
    
    await safe_send_message(update, "❌ Добавление сервера отменено")
    return ConversationHandler.END