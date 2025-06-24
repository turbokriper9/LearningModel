import pymysql
import sys
import os
import subprocess

def check_mysql_status():
    """
    Проверяет статус MySQL и пытается диагностировать проблемы
    """
    print("Диагностика MySQL:")
    
    # Проверяем, запущен ли MySQL
    try:
        result = subprocess.run(["sc", "query", "mysql"], capture_output=True, text=True)
        print(f"Статус службы MySQL: {result.stdout}")
    except Exception as e:
        print(f"Не удалось проверить статус службы MySQL: {e}")
    
    # Проверяем наличие файла my.ini в XAMPP
    xampp_paths = [
        "C:\\xampp\\mysql\\bin\\my.ini",
        "C:\\Program Files\\xampp\\mysql\\bin\\my.ini",
        "D:\\xampp\\mysql\\bin\\my.ini"
    ]
    
    for path in xampp_paths:
        if os.path.exists(path):
            print(f"Найден файл конфигурации MySQL: {path}")
            break
    else:
        print("Файл конфигурации MySQL не найден в стандартных расположениях XAMPP")

def create_database():
    """
    Создание базы данных MySQL для проекта
    """
    # Сначала проверяем статус MySQL
    check_mysql_status()
    
    try:
        # Подключение к MySQL
        print("Пытаемся подключиться к MySQL на localhost...")
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="",  # Укажите пароль, если он установлен
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("Успешное подключение к MySQL!")
        
        with connection.cursor() as cursor:
            # Проверяем существование базы данных
            cursor.execute("SHOW DATABASES LIKE 'attendance'")
            result = cursor.fetchone()
            
            if result:
                print("База данных 'attendance' уже существует.")
                choice = input("Пересоздать базу данных? (y/n): ")
                if choice.lower() == "y":
                    cursor.execute("DROP DATABASE attendance")
                    print("База данных удалена.")
                else:
                    print("Операция отменена.")
                    return
            
            # Создание базы данных
            cursor.execute("CREATE DATABASE attendance CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print("База данных 'attendance' успешно создана!")
            
        print("\nТеперь вы можете запустить приложение с помощью команды:")
        print("uvicorn app.main:app --reload")
        
    except pymysql.MySQLError as e:
        print(f"Ошибка при подключении к MySQL: {e}")
        print("\nПроверьте следующее:")
        print("1. Запущен ли сервер MySQL в XAMPP")
        print("2. Правильно ли указаны логин и пароль (по умолчанию: root, пароль пустой)")
        print("3. Нет ли конфликта портов (MySQL использует порт 3306)")
        print("\nДля решения проблемы попробуйте:")
        print("1. Перезапустите XAMPP от имени администратора")
        print("2. Проверьте логи MySQL в папке xampp\\mysql\\data\\mysql_error.log")
        print("3. Временно используйте SQLite, изменив DB_TYPE в файле app/core/config.py")
        sys.exit(1)
    finally:
        if "connection" in locals():
            connection.close()

if __name__ == "__main__":
    create_database()
