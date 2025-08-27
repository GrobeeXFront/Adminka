#!/usr/bin/env python3
"""
Модуль для управления systemd сервисами
"""

import asyncio
from typing import Tuple
from services.ssh_client import execute_server_command

async def create_systemd_service(server_id: int, user_id: int, service_name: str, 
                              bot_directory: str, bot_filename: str, username: str) -> Tuple[bool, str]:
    """Создание systemd сервиса для бота"""
    
    service_content = f"""[Unit]
Description=Telegram Bot Service - {service_name}
After=network.target

[Service]
Type=simple
User={username}
WorkingDirectory={bot_directory}
ExecStart=/usr/bin/python3 {bot_filename}
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
"""
    
    commands = [
        f"echo '{service_content}' | sudo tee /etc/systemd/system/{service_name}.service",
        f"sudo systemctl daemon-reload",
        f"sudo systemctl enable {service_name}",
        f"sudo systemctl start {service_name}"
    ]
    
    results = []
    for cmd in commands:
        success, result = await execute_server_command(server_id, user_id, cmd)
        results.append((success, result))
        if not success:
            return False, f"Ошибка при создании сервиса: {result}"
    
    return True, f"✅ Systemd сервис '{service_name}' успешно создан и запущен"

async def check_systemd_service(server_id: int, user_id: int, service_name: str) -> Tuple[bool, str]:
    """Проверка существования systemd сервиса"""
    check_cmd = f"systemctl list-unit-files | grep -E '^{service_name}\\.service'"
    success, result = await execute_server_command(server_id, user_id, check_cmd)
    
    if success and service_name in result:
        return True, "✅ Сервис существует"
    return False, "❌ Сервис не существует"

async def manage_systemd_service(server_id: int, user_id: int, service_name: str, action: str) -> Tuple[bool, str]:
    """Управление systemd сервисом"""
    actions = ['start', 'stop', 'restart', 'status', 'enable', 'disable']
    
    if action not in actions:
        return False, f"❌ Неподдерживаемое действие: {action}"
    
    cmd = f"sudo systemctl {action} {service_name}"
    success, result = await execute_server_command(server_id, user_id, cmd)
    
    if success:
        return True, f"✅ Команда '{action}' выполнена успешно"
    return False, f"❌ Ошибка выполнения '{action}': {result}"