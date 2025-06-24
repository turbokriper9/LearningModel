import pymysql
from app.core.config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME
import datetime

def test_mysql_connection():
    """
    Тестирование соединения с MySQL и запись данных напрямую
    """
    try:
        # Подключаемся к базе данных
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("Соединение с MySQL успешно!")
        
        # Проверяем существующие таблицы
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"Существующие таблицы: {tables}")
            
            # Проверяем структуру таблицы attendance
            cursor.execute("DESCRIBE attendance")
            columns = cursor.fetchall()
            print("\nСтруктура таблицы attendance:")
            for column in columns:
                print(f"  {column['Field']} ({column['Type']})")
                
            # Вставляем тестовую запись напрямую через SQL
            current_time = datetime.datetime.now()
            current_date = current_time.date()
            
            insert_query = """
            INSERT INTO attendance 
            (timestamp, count, lesson_number, date) 
            VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(insert_query, (
                current_time, 
                10,  # Тестовое количество студентов
                2,   # Тестовый номер пары
                current_date
            ))
            
            # Сохраняем изменения
            connection.commit()
            
            print("\nТестовая запись успешно добавлена!")
            
            # Проверяем, что запись действительно была добавлена
            cursor.execute("SELECT * FROM attendance ORDER BY id DESC LIMIT 1")
            last_record = cursor.fetchone()
            print(f"Последняя запись: {last_record}")
        
        connection.close()
        print("\nТест успешно завершен!")
        return True
        
    except Exception as e:
        print(f"Ошибка при работе с MySQL: {e}")
        return False

if __name__ == "__main__":
    test_mysql_connection() 