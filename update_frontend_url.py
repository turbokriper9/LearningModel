import os
import re
import sys

def update_api_url(file_path, old_url, new_url):
    """
    Заменяет все вхождения old_url на new_url в указанном файле
    """
    try:
        # Проверяем существование файла
        if not os.path.exists(file_path):
            print(f"Ошибка: Файл {file_path} не найден")
            return False
        
        # Читаем содержимое файла
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Подсчитываем количество замен
        count = content.count(old_url)
        if count == 0:
            print(f"URL {old_url} не найден в файле {file_path}")
            return False
        
        # Заменяем URL
        new_content = content.replace(old_url, new_url)
        
        # Записываем обновленное содержимое
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print(f"Успешно заменены все {count} вхождения URL в файле {file_path}")
        return True
    
    except Exception as e:
        print(f"Ошибка при обновлении URL: {e}")
        return False

def main():
    # Путь к файлу React-приложения
    file_path = "frontend/src/App.js"
    
    # Старый URL (локальный)
    old_url = "http://localhost:8000"
    
    # Если URL передан как аргумент, используем его
    if len(sys.argv) > 1:
        new_url = sys.argv[1]
    else:
        # Иначе запрашиваем у пользователя
        new_url = input("Введите новый URL API (например, https://1234-abcd.ngrok.io): ")
    
    # Проверяем формат URL
    if not new_url.startswith("http"):
        print("Ошибка: URL должен начинаться с http:// или https://")
        return
    
    # Удаляем слеш в конце URL, если он есть
    new_url = new_url.rstrip('/')
    
    # Выполняем замену
    success = update_api_url(file_path, old_url, new_url)
    
    if success:
        print("\nТеперь вы можете запустить фронтенд командой:")
        print("cd frontend && npm start")

if __name__ == "__main__":
    main() 