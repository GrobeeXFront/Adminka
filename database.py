#!/usr/bin/env python3
"""
Модуль для работы с базой данных
"""

import sqlite3
from typing import List, Tuple, Dict, Any, Optional
from config import DB_PATH, MAX_SERVERS_PER_USER

def get_db_connection():
    """Получить соединение с базой данных"""
    return sqlite3.connect(DB_PATH)

def init_database():
    """Инициализация базы данных"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_servers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        server_name TEXT NOT NULL,
        hostname TEXT NOT NULL,
        port INTEGER DEFAULT 22,
        username TEXT NOT NULL,
        password TEXT,
        private_key TEXT,
        bot_directory TEXT DEFAULT "/home",
        bot_filename TEXT DEFAULT "bot.py",
        service_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, server_name)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS server_commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER NOT NULL,
        command TEXT NOT NULL,
        result TEXT,
        success BOOLEAN,
        executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (server_id) REFERENCES user_servers (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def add_user_server(user_id: int, server_name: str, hostname: str, username: str, 
                   password: Optional[str] = None, private_key: Optional[str] = None,
                   port: int = 22, bot_directory: str = "/home", 
                   bot_filename: str = "bot.py") -> Tuple[bool, str]:
    """Добавить сервер пользователя"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM user_servers WHERE user_id = ?", (user_id,))
        server_count = cursor.fetchone()[0]
        
        if server_count >= MAX_SERVERS_PER_USER:
            return False, f"❌ Превышен лимит серверов ({MAX_SERVERS_PER_USER})"
        
        cursor.execute("SELECT COUNT(*) FROM user_servers WHERE user_id = ? AND server_name = ?", 
                      (user_id, server_name))
        if cursor.fetchone()[0] > 0:
            return False, "❌ Сервер с таким именем уже существует"
        
        cursor.execute('''
        INSERT INTO user_servers 
        (user_id, server_name, hostname, port, username, password, private_key, bot_directory, bot_filename)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, server_name, hostname, port, username, password, private_key, bot_directory, bot_filename))
        
        conn.commit()
        return True, "✅ Сервер успешно добавлен"
        
    except Exception as e:
        conn.rollback()
        return False, f"❌ Ошибка добавления сервера: {str(e)}"
    finally:
        conn.close()

def get_user_servers(user_id: int) -> List[Dict[str, Any]]:
    """Получить список серверов пользователя"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id, server_name, hostname, port, username, bot_directory, bot_filename
    FROM user_servers 
    WHERE user_id = ? 
    ORDER BY created_at DESC
    ''', (user_id,))
    
    servers = []
    for row in cursor.fetchall():
        servers.append({
            'id': row[0],
            'name': row[1],
            'hostname': row[2],
            'port': row[3],
            'username': row[4],
            'directory': row[5],
            'filename': row[6]
        })
    
    conn.close()
    return servers

def get_server_config(server_id: int, user_id: int) -> Optional[Dict[str, Any]]:
    """Получить конфигурацию сервера"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT id, server_name, hostname, port, username, password, private_key, bot_directory, bot_filename
    FROM user_servers 
    WHERE id = ? AND user_id = ?
    ''', (server_id, user_id))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'name': row[1],
            'hostname': row[2],
            'port': row[3],
            'username': row[4],
            'password': row[5],
            'private_key': row[6],
            'bot_directory': row[7],
            'bot_filename': row[8]
        }
    return None

def update_user_server(server_id: int, user_id: int, **kwargs) -> Tuple[bool, str]:
    """Обновить данные сервера"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Проверяем существование сервера
        cursor.execute('SELECT id FROM user_servers WHERE id = ? AND user_id = ?', 
                      (server_id, user_id))
        if not cursor.fetchone():
            return False, "❌ Сервер не найден"
        
        # Формируем запрос обновления
        update_fields = []
        update_values = []
        
        allowed_fields = ['server_name', 'hostname', 'port', 'username', 
                        'password', 'private_key', 'bot_directory', 'bot_filename']
        
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                update_fields.append(f"{field} = ?")
                update_values.append(value)
        
        if not update_fields:
            return False, "❌ Нет полей для обновления"
        
        update_values.append(server_id)
        update_values.append(user_id)
        
        query = f'''
        UPDATE user_servers 
        SET {', '.join(update_fields)}
        WHERE id = ? AND user_id = ?
        '''
        
        cursor.execute(query, update_values)
        conn.commit()
        
        return True, "✅ Сервер успешно обновлен"
        
    except Exception as e:
        conn.rollback()
        return False, f"❌ Ошибка обновления сервера: {str(e)}"
    finally:
        conn.close()

def delete_user_server(server_id: int, user_id: int) -> Tuple[bool, str]:
    """Удалить сервер пользователя"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM user_servers WHERE id = ? AND user_id = ?', 
                      (server_id, user_id))
        
        if cursor.rowcount == 0:
            return False, "❌ Сервер не найден"
        
        conn.commit()
        return True, "✅ Сервер успешно удален"
        
    except Exception as e:
        conn.rollback()
        return False, f"❌ Ошибка удаления сервера: {str(e)}"
    finally:
        conn.close()