import pymysql

def check_tables():
    """
    Проверка таблиц в базе данных MySQL напрямую
    """
    try:
        # Подключение к MySQL
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            db="attendance",
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("✓ Успешное подключение к базе данных MySQL!")
        
        with connection.cursor() as cursor:
            # Показать все таблицы
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                print(f"✓ В базе данных найдено {len(tables)} таблиц:")
                for table_info in tables:
                    table_name = list(table_info.values())[0]
                    print(f"  - {table_name}")
                    
                    # Показать структуру таблицы
                    cursor.execute(f"DESCRIBE {table_name}")
                    columns = cursor.fetchall()
                    print(f"    Колонки таблицы {table_name}:")
                    for column in columns:
                        print(f"      {column['Field']} ({column['Type']})")
            else:
                print("✗ В базе данных нет таблиц.")
        
    except pymysql.MySQLError as e:
        print(f"✗ Ошибка при подключении к MySQL: {e}")
    finally:
        if "connection" in locals():
            connection.close()

if __name__ == "__main__":
    check_tables() 