import pymysql
import sys

def create_database():
    """
    Создание базы данных MySQL для проекта
    """
    try:
        # Подключение к MySQL
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
        sys.exit(1)
    finally:
        if "connection" in locals():
            connection.close()

if __name__ == "__main__":
    create_database()
