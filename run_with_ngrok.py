import uvicorn
from pyngrok import ngrok
import time
import qrcode
from PIL import Image
import os

# Порты для наших сервисов
API_PORT = 8000
FRONTEND_PORT = 3000

# Функция для генерации QR-кода
def generate_qr_code(url, filename):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    print(f"QR-код сохранен в файл: {filename}")

# Запускаем туннель для API
api_tunnel = ngrok.connect(API_PORT, "http")
api_public_url = api_tunnel.public_url
print(f"API доступно по адресу: {api_public_url}")

# Запускаем туннель для фронтенда
frontend_tunnel = ngrok.connect(FRONTEND_PORT, "http")
frontend_public_url = frontend_tunnel.public_url
print(f"Фронтенд доступен по адресу: {frontend_public_url}")

# Генерируем QR-коды
generate_qr_code(api_public_url, "api_qrcode.png")
generate_qr_code(frontend_public_url, "frontend_qrcode.png")

# Объединяем QR-коды в один файл с надписями
try:
    api_img = Image.open("api_qrcode.png")
    frontend_img = Image.open("frontend_qrcode.png")
    
    # Создаем новое изображение, которое поместит оба QR-кода рядом
    combined_width = api_img.width + frontend_img.width + 50  # добавляем отступ
    combined_height = max(api_img.height, frontend_img.height) + 60  # место для текста
    
    combined_img = Image.new('RGB', (combined_width, combined_height), color='white')
    
    # Вставляем QR-коды
    combined_img.paste(api_img, (0, 50))
    combined_img.paste(frontend_img, (api_img.width + 50, 50))
    
    # Сохраняем
    combined_img.save("qrcodes.png")
    print("Сгенерирован общий файл с QR-кодами: qrcodes.png")
except Exception as e:
    print(f"Ошибка при объединении QR-кодов: {e}")

print("\nВНИМАНИЕ: Необходимо вручную изменить URL в React-приложении на новый API URL!")
print(f"В файле frontend/src/App.js замените все URL http://localhost:8000 на {api_public_url}")
print("После этого запустите npm start в директории frontend\n")

print("Сервисы доступны по следующим URL:")
print(f"API: {api_public_url}")
print(f"Фронтенд: {frontend_public_url}")
print("\nНажмите Ctrl+C для остановки туннелей...")

try:
    # Запускаем API
    uvicorn.run("app.main:app", host="0.0.0.0", port=API_PORT)
except KeyboardInterrupt:
    print("Завершение работы туннелей...")
    ngrok.kill() 