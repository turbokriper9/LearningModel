import pymysql
import sys

def check_mysql_connection():
    """
    Проверка подключения к MySQL
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
        
        print("✓ Успешное подключение к серверу MySQL!")
        
        with connection.cursor() as cursor:
            # Проверяем существование базы данных
            cursor.execute("SHOW DATABASES LIKE 'attendance'")
            result = cursor.fetchone()
            
            if result:
                print("✓ База данных 'attendance' существует.")
                
                # Подключаемся к базе данных
                connection.select_db('attendance')
                
                # Проверяем таблицы
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                
                if tables:
                    print("✓ В базе данных есть следующие таблицы:")
                    for table in tables:
                        print(f"  - {list(table.values())[0]}")
                else:
                    print("✗ В базе данных 'attendance' нет таблиц.")
                    print("  Запустите миграции или создайте таблицы.")
            else:
                print("✗ База данных 'attendance' не существует.")
                print("  Запустите скрипт create_mysql_db.py для её создания.")
        
    except pymysql.MySQLError as e:
        print(f"✗ Ошибка при подключении к MySQL: {e}")
        sys.exit(1)
    finally:
        if "connection" in locals():
            connection.close()

if __name__ == "__main__":
    check_mysql_connection() 