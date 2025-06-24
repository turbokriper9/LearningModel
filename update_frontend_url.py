import os
import re
import sys
import socket

def get_local_ip():
    """Получение локального IP-адреса компьютера"""
    try:
        # Создаем временное соединение для определения IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"  # В случае ошибки возвращаем localhost

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
        # Получаем локальный IP-адрес
        local_ip = get_local_ip()
        new_url = f"http://{local_ip}:8000"
        print(f"Используем локальный IP-адрес: {local_ip}")
    
    # Проверяем формат URL
    if not new_url.startswith("http"):
        print("Ошибка: URL должен начинаться с http:// или https://")
        return
    
    # Удаляем слеш в конце URL, если он есть
    new_url = new_url.rstrip('/')
    
    # Выполняем замену
    success = update_api_url(file_path, old_url, new_url)
    
    if success:
        print("\nURL API успешно обновлен на:", new_url)
        print("\nТеперь вы можете запустить фронтенд командой:")
        print("cd frontend && npm start")

if __name__ == "__main__":
    main() 