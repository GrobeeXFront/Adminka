# SSH Админ-Бот для управления серверами (далее [adminka])

🤖 Telegram бот для удаленного управления серверами через SSH

## 📋 Возможности

### Управление серверами
- ✅ Добавление/удаление серверов
- ✅ Редактирование параметров серверов
- ✅ Просмотр списка серверов
- ✅ Проверка статуса серверов

### Управление ботами
- ✅ Запуск/остановка Python ботов
- ✅ Просмотр логов ботов
- ✅ Автоматическое создание systemd сервисов
- ✅ Мониторинг состояния ботов

### Безопасность
- ✅ Белый список разрешенных команд
- ✅ Проверка безопасности выполняемых команд
- ✅ Изоляция пользовательских данных
- ✅ Логирование всех операций

## 🚀 Установка

### Требования
- Python 3.8+
- SSH доступ к управляемым серверам
- Telegram Bot Token

### Установка зависимостей
```bash
pip install python-telegram-bot paramiko

### Каталог 
adminka/
├── main.py
├── config.py
├── help.py
├── database.py
├── services/ (подключение по ssh)
│   ├── __init__.py
│   ├── ssh_client.py
│   └── bot_checker.py
├── utils/
│   ├── __init__.py
│   ├── logging.py
│   ├── decorators.py
│   └── helpers.py
├── conversation/
│   ├── __init__.py
│   ├── states.py
│   └── storage.py
├── handlers/
│   ├── __init__.py
│   ├── base.py
│   ├── server/
│   │   ├── __init__.py
│   │   ├── add.py
│   │   ├── edit.py
│   │   ├── delete.py
│   │   └── list.py
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── start.py
│   │   ├── stop.py
│   │   ├── status.py
│   │   └── logs.py
│   └── command/
│       ├── __init__.py
│       └── execute.py
└── logs/
    └── (логи будут создаваться автоматически)