#!/usr/bin/env python
"""
Скрипт для настройки MySQL базы данных
"""
import sys
import os
import pymysql
from app.core.config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_mysql_database():
    """
    Функция для создания базы данных MySQL, если она не существует
    """
    try:
        # Подключаемся к серверу MySQL (без указания конкретной БД)
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Проверяем, существует ли база данных
            cursor.execute(f"SHOW DATABASES LIKE '{DB_NAME}'")
            result = cursor.fetchone()
            
            if not result:
                print(f"База данных '{DB_NAME}' не существует. Создаем...")
                # Создаем базу данных с правильной кодировкой
                cursor.execute(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print(f"База данных '{DB_NAME}' успешно создана!")
            else:
                print(f"База данных '{DB_NAME}' уже существует.")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"Ошибка при настройке базы данных: {e}")
        return False

if __name__ == "__main__":
    print("Настройка базы данных MySQL...")
    success = setup_mysql_database()
    
    if success:
        print("Настройка базы данных завершена успешно.")
        
        # Теперь создаем таблицы через SQLAlchemy
        try:
            from app.core.database import init_db
            print("Создание таблиц через SQLAlchemy...")
            init_db()
            print("Таблицы успешно созданы!")
        except Exception as e:
            print(f"Ошибка при создании таблиц: {e}")
    else:
        print("Не удалось настроить базу данных.")

try:
    # Импортируем функцию для создания таблиц
    from utils.create_tables import create_tables
    create_tables()
    
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Убедитесь, что файлы utils/create_mysql_db.py и utils/create_tables.py существуют")
    sys.exit(1)
except Exception as e:
    print(f"Произошла ошибка: {e}")
    sys.exit(1) 