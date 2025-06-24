import sqlite3
import os
import datetime

print("Очистка тестовых данных из базы данных...")

# Проверяем наличие файла базы данных
if not os.path.exists("attendance.db"):
    print("Файл базы данных не найден!")
    exit(1)

# Подключаемся к базе данных
conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()

# Получаем количество записей до удаления
cursor.execute("SELECT COUNT(*) FROM attendance")
count_before = cursor.fetchone()[0]
print(f"Количество записей до удаления: {count_before}")

# Удаляем все записи из таблицы attendance
cursor.execute("DELETE FROM attendance")
conn.commit()

# Проверяем количество записей после удаления
cursor.execute("SELECT COUNT(*) FROM attendance")
count_after = cursor.fetchone()[0]
print(f"Количество записей после удаления: {count_after}")

print(f"Удалено записей: {count_before - count_after}")

# Сбрасываем автоинкремент
cursor.execute("DELETE FROM sqlite_sequence WHERE name='attendance'")
conn.commit()

print("Автоинкремент сброшен.")

# Закрываем соединение
conn.close()

print("Очистка завершена успешно!") 