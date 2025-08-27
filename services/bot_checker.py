#!/usr/bin/env python3
"""
Модуль для проверки статуса бота
"""

import asyncio
from services.ssh_client import execute_server_command

async def check_bot_status(server_id: int, user_id: int, bot_filename: str) -> str:
    """Проверка статуса бота на сервере"""
    try:
        # Команда для проверки процессов бота
        check_command = f"pgrep -f 'python3.*{bot_filename}'"
        success, result = await execute_server_command(server_id, user_id, check_command)
        
        if success and result.strip():
            pids = result.strip().split('\n')
            pid_count = len(pids)
            
            # Дополнительная проверка через systemctl если возможно
            service_check = f"systemctl is-active bot 2>/dev/null || echo 'inactive'"
            service_success, service_result = await execute_server_command(server_id, user_id, service_check)
            
            if service_success and 'active' in service_result:
                return f"✅ Запущен (systemd, {pid_count} процессов)"
            else:
                return f"✅ Запущен ({pid_count} процессов)"
        else:
            return "❌ Остановлен"
            
    except Exception:
        return "❓ Неизвестно (ошибка проверки)"