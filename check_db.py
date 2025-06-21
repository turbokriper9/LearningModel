import sqlite3
import os

print("Текущая директория:", os.getcwd())
print("Проверка наличия файла attendance.db:", os.path.exists("attendance.db"))

try:
    conn = sqlite3.connect('attendance.db')
    cursor = conn.cursor()
    
    # Получаем список таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Таблицы в базе данных:", tables)
    
    # Проверяем таблицу attendance, если она существует
    if ('attendance',) in tables:
        cursor.execute("SELECT COUNT(*) FROM attendance")
        count = cursor.fetchone()[0]
        print(f"Количество записей в таблице attendance: {count}")
        
        # Выводим последние 5 записей
        cursor.execute("SELECT id, timestamp, count FROM attendance ORDER BY timestamp DESC LIMIT 5")
        records = cursor.fetchall()
        print("Последние записи:")
        for record in records:
            print(f"ID: {record[0]}, Время: {record[1]}, Количество: {record[2]}")
    else:
        print("Таблица attendance не найдена")
    
    conn.close()
except Exception as e:
    print(f"Ошибка при работе с базой данных: {str(e)}") 