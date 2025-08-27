#!/usr/bin/env python3
"""
Модуль для SSH подключений и выполнения команд
"""

import paramiko
import asyncio
from typing import Tuple, Dict, Any
from config import SSH_TIMEOUT, ALLOWED_SSH_COMMANDS

def is_safe_command(command: str) -> bool:
    """Проверка безопасности команды"""
    command_lower = command.lower().strip()
    
    # Разрешаем базовые команды для статуса системы
    basic_commands = ['uptime', 'free -h', 'df -h', 'whoami', 'pwd']
    if command_lower in basic_commands:
        return True
    
    # Разрешаем команды с параметрами для статуса
    if any(command_lower.startswith(cmd) for cmd in ['free ', 'df ', 'cat /proc/loadavg']):
        return True
    
    # Разрешаем команды для управления процессами
    process_commands = ['ps ', 'pgrep ', 'pkill -f ', 'kill ']
    if any(command_lower.startswith(cmd) for cmd in process_commands):
        # Проверяем, что это не опасные варианты
        dangerous_patterns = ['-9', 'killall', 'rm -rf']
        if not any(pattern in command_lower for pattern in dangerous_patterns):
            return True
    
    # Разрешаем команды для управления сервисами
    if any(command_lower.startswith(cmd) for cmd in ['systemctl ', 'journalctl ']):
        return True
    
    # Разрешаем команды для работы с файлами (ограниченно)
    if any(command_lower.startswith(cmd) for cmd in ['tail ', 'cd ', 'ls ', 'cat ']):
        return True
    
    # Разрешаем screen команды
    if command_lower.startswith('screen '):
        return True
    
    # Разрешаем команды для запуска/остановки ботов
    bot_commands = ['nohup python', 'python3 ', 'pkill -f python']
    if any(cmd in command_lower for cmd in bot_commands):
        # Проверяем, что это не опасные варианты
        dangerous_patterns = ['-9', 'killall', 'rm -rf', '; rm', '| rm']
        if not any(pattern in command_lower for pattern in dangerous_patterns):
            return True
    
    # Запрещаем явно опасные команды
    dangerous_patterns = [
        'rm -rf', 'dd if=', 'mkfs', 'shutdown', 'reboot', 
        'halt', 'poweroff', 'chmod 777', ':(){:|:&};:',
        'mv / /dev/null', '> /dev/sda', 'mkfs.ext3 /dev/sda1',
        'wget ', 'curl ', 'bash -c', 'sh -c'
    ]
    
    if any(pattern in command_lower for pattern in dangerous_patterns):
        return False
    
    # Разрешаем команды из белого списка
    first_word = command_lower.split()[0] if command_lower else ''
    return first_word in ALLOWED_SSH_COMMANDS

async def execute_ssh_command(server_config: Dict[str, Any], command: str) -> Tuple[bool, str]:
    """Выполнение команды по SSH"""
    ssh = None
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        connect_args = {
            'hostname': server_config['hostname'],
            'port': server_config.get('port', 22),
            'username': server_config['username'],
            'timeout': SSH_TIMEOUT
        }
        
        if server_config.get('private_key'):
            key = paramiko.RSAKey.from_private_key_file(server_config['private_key'])
            connect_args['pkey'] = key
        elif server_config.get('password'):
            connect_args['password'] = server_config['password']
        else:
            return False, "❌ Не указаны учетные данные для подключения"
        
        ssh.connect(**connect_args)
        
        # Устанавливаем рабочий каталог если указан
        if server_config.get('bot_directory'):
            full_command = f"cd {server_config['bot_directory']} && {command}"
        else:
            full_command = command
        
        # Выполняем команду с таймаутом
        stdin, stdout, stderr = ssh.exec_command(full_command, timeout=SSH_TIMEOUT)
        exit_code = stdout.channel.recv_exit_status()
        
        output = stdout.read().decode('utf-8', errors='ignore').strip()
        error = stderr.read().decode('utf-8', errors='ignore').strip()
        
        if exit_code == 0:
            return True, output if output else "✅ Команда выполнена успешно"
        else:
            error_msg = error if error else f"❌ Ошибка выполнения (код: {exit_code})"
            return False, error_msg
            
    except paramiko.AuthenticationException:
        return False, "❌ Ошибка аутентификации SSH"
    except paramiko.SSHException as e:
        return False, f"❌ Ошибка SSH: {str(e)}"
    except Exception as e:
        return False, f"❌ Ошибка подключения: {str(e)}"
    finally:
        if ssh:
            ssh.close()

async def execute_server_command(server_id: int, user_id: int, command: str) -> Tuple[bool, str]:
    """Выполнить команду на сервере"""
    from database import get_server_config
    
    server_config = get_server_config(server_id, user_id)
    if not server_config:
        return False, "❌ Сервер не найден"
    
    if not is_safe_command(command):
        return False, f"❌ Команда не разрешена для безопасности: {command}"
    
    try:
        # Выполняем команду
        success, result = await execute_ssh_command(server_config, command)
        
        # Сохраняем результат в базу
        from database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO server_commands (server_id, command, result, success)
            VALUES (?, ?, ?, ?)
            ''', (server_id, command, result, success))
            conn.commit()
        except Exception as e:
            pass  # Логируем, но не прерываем выполнение
        finally:
            conn.close()
        
        return success, result
        
    except Exception as e:
        return False, f"❌ Ошибка выполнения: {str(e)}"