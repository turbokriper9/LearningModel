import pymysql
from app.core.config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME

def update_mysql_schema():
    """
    Обновляет схему таблицы attendance, добавляя необходимые колонки
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
        
        # Проверяем структуру таблицы attendance
        with connection.cursor() as cursor:
            print("Проверяем текущую структуру таблицы attendance...")
            cursor.execute("DESCRIBE attendance")
            columns = cursor.fetchall()
            
            column_names = [col['Field'] for col in columns]
            print(f"Текущие колонки: {column_names}")
            
            # Добавляем колонку lesson_number, если она отсутствует
            if 'lesson_number' not in column_names:
                print("Добавляем колонку lesson_number...")
                cursor.execute("ALTER TABLE attendance ADD COLUMN lesson_number INT NULL")
                print("Колонка lesson_number добавлена!")
            else:
                print("Колонка lesson_number уже существует.")
            
            # Добавляем колонку date, если она отсутствует
            if 'date' not in column_names:
                print("Добавляем колонку date...")
                cursor.execute("ALTER TABLE attendance ADD COLUMN date DATE NULL")
                print("Колонка date добавлена!")
            else:
                print("Колонка date уже существует.")
            
            # Обновляем существующие записи, устанавливая дату из timestamp
            print("Обновляем существующие записи...")
            cursor.execute("""
                UPDATE attendance 
                SET date = DATE(timestamp) 
                WHERE date IS NULL
            """)
            print("Записи обновлены!")
            
            # Сохраняем изменения
            connection.commit()
            
            # Проверяем обновленную структуру
            cursor.execute("DESCRIBE attendance")
            updated_columns = cursor.fetchall()
            print("\nОбновленная структура таблицы:")
            for column in updated_columns:
                print(f"  {column['Field']} ({column['Type']})")
        
        connection.close()
        print("\nСхема успешно обновлена!")
        return True
        
    except Exception as e:
        print(f"Ошибка при обновлении схемы: {e}")
        return False

if __name__ == "__main__":
    update_mysql_schema() 