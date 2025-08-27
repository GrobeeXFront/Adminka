#!/usr/bin/env python3
"""
Инициализация обработчиков
"""

from .base import (
    start_handler, help_handler
)
from .server.add import (
    add_server_start, add_server_name, add_server_hostname,
    add_server_username, add_server_password, add_server_port,
    add_server_directory, add_server_filename, add_server_cancel
)
from .server.edit import (
    edit_server_start, edit_server_choose, edit_server_value, edit_server_cancel
)
from .server.delete import delete_server_handler
from .server.list import my_servers_handler  # ← Импорт из правильного места
from .bot.start import start_bot_handler
from .bot.stop import stop_bot_handler
from .bot.status import server_status_handler
from .bot.logs import bot_logs_handler
from .command.execute import run_command_handler

__all__ = [
    'start_handler', 'help_handler', 'my_servers_handler',  # ← Теперь есть
    'add_server_start', 'add_server_name', 'add_server_hostname',
    'add_server_username', 'add_server_password', 'add_server_port',
    'add_server_directory', 'add_server_filename', 'add_server_cancel',
    'edit_server_start', 'edit_server_choose', 'edit_server_value', 'edit_server_cancel',
    'delete_server_handler', 'server_status_handler', 'start_bot_handler',
    'stop_bot_handler', 'bot_logs_handler', 'run_command_handler'
]