import os
from typing import ClassVar

# Выберите тип базы данных: 'sqlite' или 'mysql'
DB_TYPE = "mysql"

# Настройки подключения к базе данных
if DB_TYPE == "sqlite":
    # SQLite - простая локальная база данных
    DATABASE_URL = "sqlite:///./attendance.db"
else:
    # MySQL - для продакшена
    # Укажите правильные учетные данные для вашей установки MySQL
    DB_USER = "root"
    DB_PASSWORD = ""  # Укажите пароль, если он установлен
    DB_HOST = "localhost"
    DB_NAME = "attendance"
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Экспортируем URL для использования в других модулях
settings = {"DATABASE_URL": DATABASE_URL}