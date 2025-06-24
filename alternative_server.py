import os
import subprocess
import socket
import qrcode
from PIL import Image, ImageDraw, ImageFont
import sys
import time

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

def generate_qr_code(url, filename):
    """Генерация QR-кода"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Сохраняем QR-код
    img.save(filename)
    print(f"QR-код сохранен в файл: {filename}")
    return img

def generate_info_image(api_url, frontend_url):
    """Создает информационное изображение с QR-кодами и инструкциями"""
    try:
        # Генерируем QR-коды
        api_qr = generate_qr_code(api_url, "local_api_qrcode.png")
        frontend_qr = generate_qr_code(frontend_url, "local_frontend_qrcode.png")
        
        # Размеры QR-кодов
        qr_width, qr_height = api_qr.size
        
        # Создаем новое изображение, которое вместит оба QR-кода и текст
        img_width = max(800, qr_width * 2 + 100)
        img_height = qr_height + 200  # Дополнительное место для текста
        
        # Создаем пустое изображение
        combined_img = Image.new('RGB', (img_width, img_height), color='white')
        
        # Вставляем QR-коды
        combined_img.paste(api_qr, (50, 150))
        combined_img.paste(frontend_qr, (qr_width + 100, 150))
        
        # Добавляем текст
        draw = ImageDraw.Draw(combined_img)
        
        # Заголовок
        try:
            # Пробуем использовать встроенный шрифт
            font_large = ImageFont.truetype("arial.ttf", 24)
            font_medium = ImageFont.truetype("arial.ttf", 18)
            font_small = ImageFont.truetype("arial.ttf", 14)
        except Exception:
            # Если не удалось, используем шрифт по умолчанию
            font_large = ImageFont.load_default()
            font_medium = font_large
            font_small = font_large
        
        # Заголовок
        draw.text((img_width//2, 20), "Система учета посещаемости студентов", 
                fill="black", font=font_large, anchor="mt")
        
        # Подписи к QR-кодам
        draw.text((qr_width//2 + 50, 120), "API", 
                fill="black", font=font_medium, anchor="mm")
        draw.text((qr_width + 100 + qr_width//2, 120), "Фронтенд", 
                fill="black", font=font_medium, anchor="mm")
        
        # URL под QR-кодами
        draw.text((qr_width//2 + 50, qr_height + 170), api_url, 
                fill="blue", font=font_small, anchor="mm")
        draw.text((qr_width + 100 + qr_width//2, qr_height + 170), frontend_url, 
                fill="blue", font=font_small, anchor="mm")
        
        # Сохраняем итоговое изображение
        combined_img.save("local_network_access.png")
        print("Информационное изображение сохранено в файл: local_network_access.png")
        
        # Возвращаем пути к файлам
        return {
            "api_qr": "local_api_qrcode.png",
            "frontend_qr": "local_frontend_qrcode.png",
            "combined": "local_network_access.png"
        }
    except Exception as e:
        print(f"Ошибка при создании информационного изображения: {e}")
        return None

def update_frontend_api_url(ip_address, port=8000):
    """Обновляет URL API в React-приложении"""
    try:
        file_path = "frontend/src/App.js"
        old_url = "http://localhost:8000"
        new_url = f"http://{ip_address}:{port}"
        
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

def run_command(command, background=True):
    """Запускает команду в отдельном окне"""
    try:
        if background:
            if sys.platform == 'win32':
                # Windows - запускаем в отдельном окне
                subprocess.Popen(f'start cmd /k "{command}"', shell=True)
            else:
                # Linux/Mac
                subprocess.Popen(command, shell=True, start_new_session=True)
        else:
            # Синхронный запуск
            subprocess.run(command, shell=True)
    except Exception as e:
        print(f"Ошибка при запуске команды: {e}")

def main():
    print("\n=== ЗАПУСК СИСТЕМЫ УЧЕТА ПОСЕЩАЕМОСТИ В ЛОКАЛЬНОЙ СЕТИ ===\n")
    
    # Получаем локальный IP-адрес
    local_ip = get_local_ip()
    print(f"Локальный IP-адрес: {local_ip}")
    
    # Порты для API и фронтенда
    api_port = 8000
    frontend_port = 3000
    
    # URL для доступа
    api_url = f"http://{local_ip}:{api_port}"
    frontend_url = f"http://{local_ip}:{frontend_port}"
    
    print(f"API будет доступен по адресу: {api_url}")
    print(f"Фронтенд будет доступен по адресу: {frontend_url}")
    
    # Обновляем URL API в React-приложении
    print("\nОбновление URL API в React-приложении...")
    if update_frontend_api_url(local_ip, api_port):
        print("URL успешно обновлен")
    else:
        print("Ошибка при обновлении URL")
        confirm = input("Продолжить без обновления URL? (y/n): ")
        if confirm.lower() != 'y':
            return
    
    # Генерируем QR-коды и информационное изображение
    print("\nГенерация QR-кодов...")
    qr_files = generate_info_image(api_url, frontend_url)
    
    if qr_files:
        print("\nQR-коды успешно сгенерированы")
        print(f"- API QR-код: {qr_files['api_qr']}")
        print(f"- Фронтенд QR-код: {qr_files['frontend_qr']}")
        print(f"- Информационное изображение: {qr_files['combined']}")
        
        # Открываем изображение
        try:
            if sys.platform == 'win32':
                os.system(f'start {qr_files["combined"]}')
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open {qr_files["combined"]}')
            else:  # Linux
                os.system(f'xdg-open {qr_files["combined"]}')
        except Exception:
            pass
    
    # Запускаем серверы
    print("\nЗапуск серверов...")
    print("1. Запуск API сервера...")
    run_command("python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    
    # Даем время на запуск API
    time.sleep(2)
    
    print("2. Запуск фронтенда...")
    run_command("cd frontend && npm start")
    
    print("\n=== ИНСТРУКЦИИ ===")
    print("1. Система запущена и доступна в локальной сети")
    print("2. Для доступа отсканируйте QR-код или введите URL вручную:")
    print(f"   - API: {api_url}")
    print(f"   - Фронтенд: {frontend_url}")
    print("3. Для работы системы все устройства должны быть в одной WiFi сети")
    print("4. Для остановки сервера закройте окна терминалов или нажмите Ctrl+C в них")
    
    print("\nНажмите Ctrl+C для выхода из этого скрипта (серверы продолжат работать)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nЗавершение работы...")

if __name__ == "__main__":
    main() 