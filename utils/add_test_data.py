import sqlite3
import datetime
import random

# Подключаемся к базе данных
conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()

# Проверяем, существует ли таблица attendance
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='attendance'")
if not cursor.fetchone():
    print("Таблица attendance не найдена, создаем...")
    cursor.execute('''
    CREATE TABLE attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        count INTEGER
    )
    ''')
    conn.commit()

# Добавляем тестовые данные
print("Добавляем тестовые данные...")

# Получаем текущее время
now = datetime.datetime.now()

# Добавляем записи за последние 2 часа с интервалом в 5 минут
for i in range(24):
    # Время: текущее время минус i*5 минут
    timestamp = now - datetime.timedelta(minutes=i*5)
    
    # Количество людей: случайное число от 1 до 10
    count = random.randint(1, 10)
    
    # Добавляем запись
    cursor.execute(
        "INSERT INTO attendance (timestamp, count) VALUES (?, ?)",
        (timestamp, count)
    )

# Сохраняем изменения
conn.commit()

# Проверяем, что данные добавлены
cursor.execute("SELECT COUNT(*) FROM attendance WHERE count > 0")
count = cursor.fetchone()[0]
print(f"Всего записей с ненулевым количеством: {count}")

# Выводим последние 5 записей
cursor.execute("SELECT id, timestamp, count FROM attendance ORDER BY timestamp DESC LIMIT 5")
records = cursor.fetchall()
print("Последние записи:")
for record in records:
    print(f"ID: {record[0]}, Время: {record[1]}, Количество: {record[2]}")

# Закрываем соединение
conn.close()

print("Готово! Тестовые данные добавлены в базу данных.") 