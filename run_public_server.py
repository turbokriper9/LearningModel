import os
import subprocess
import sys
import time
import threading
from pyngrok import ngrok
from pyngrok.exception import PyngrokNgrokError
from setup_ngrok import setup_ngrok_auth

def print_colored(text, color):
    """Печать цветного текста в консоли"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'end': '\033[0m'
    }
    print(f"{colors.get(color, '')}{text}{colors['end']}")

def run_command(command, cwd=None, background=False):
    """Запуск команды с выводом в консоль"""
    try:
        if background:
            if sys.platform == 'win32':
                # Windows - используем start для запуска в отдельном окне
                full_command = f'start cmd /k "{command}"'
                return subprocess.Popen(full_command, shell=True, cwd=cwd)
            else:
                # Linux/Mac - используем новый терминал
                return subprocess.Popen(command, shell=True, cwd=cwd, start_new_session=True)
        else:
            # Синхронный запуск
            process = subprocess.Popen(command, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                print_colored(f"Ошибка при выполнении команды: {command}", "red")
                print_colored(stderr, "red")
                return False
                
            print(stdout)
            return True
    except Exception as e:
        print_colored(f"Ошибка при запуске команды {command}: {e}", "red")
        return False

def check_dependencies():
    """Проверка и установка необходимых зависимостей"""
    dependencies = [
        ("pyngrok", "pip install pyngrok"),
        ("qrcode[pil]", "pip install qrcode[pil]"),
    ]
    
    for package, install_cmd in dependencies:
        try:
            __import__(package.split('[')[0])
            print_colored(f"✓ {package} уже установлен", "green")
        except ImportError:
            print_colored(f"! Установка {package}...", "yellow")
            run_command(install_cmd)

def check_ngrok_auth():
    """Проверка настройки аутентификации ngrok"""
    try:
        # Пытаемся получить информацию о туннелях - это вызовет ошибку, если нет токена
        tunnels = ngrok.get_tunnels()
        return True
    except PyngrokNgrokError as e:
        if "authentication failed" in str(e).lower():
            print_colored("! Не настроен токен аутентификации ngrok", "red")
            print_colored("Для использования ngrok требуется настроить токен аутентификации.", "yellow")
            
            setup_token = input("Настроить токен сейчас? (y/n): ")
            if setup_token.lower() == 'y':
                return setup_ngrok_auth()
            else:
                print_colored("Без настройки токена ngrok публичный доступ невозможен.", "red")
                return False
        else:
            # Если ошибка не связана с аутентификацией, считаем, что токен настроен
            return True
    except Exception:
        # В случае других ошибок предполагаем, что токен может быть настроен
        return True

def main():
    print_colored("\n=== ЗАПУСК СИСТЕМЫ УЧЕТА ПОСЕЩАЕМОСТИ С ПУБЛИЧНЫМ ДОСТУПОМ ===\n", "cyan")
    
    # Проверяем и устанавливаем зависимости
    print_colored("1. Проверка зависимостей...", "yellow")
    check_dependencies()
    
    # Проверяем настройку токена ngrok
    print_colored("\n2. Проверка настройки ngrok...", "yellow")
    if not check_ngrok_auth():
        print_colored("\nНевозможно продолжить без настройки токена ngrok.", "red")
        print_colored("Пожалуйста, запустите 'setup_ngrok.bat' для настройки токена.", "yellow")
        input("\nНажмите Enter для выхода...")
        return
    
    # Запускаем сервер API через ngrok
    print_colored("\n3. Запуск API сервера с туннелем ngrok...", "yellow")
    api_process = run_command("python run_with_ngrok.py", background=True)
    
    # Даем время на инициализацию туннелей
    print_colored("   Ожидание инициализации туннелей (10 секунд)...", "blue")
    time.sleep(10)
    
    # Запрашиваем URL API у пользователя
    print_colored("\n4. Обновление URL API в React-приложении:", "yellow")
    api_url = input("   Введите URL API из вывода run_with_ngrok.py: ")
    
    # Обновляем URL в React-приложении
    if api_url:
        run_command(f"python update_frontend_url.py {api_url}")
    else:
        print_colored("   URL не введен, пропускаем обновление...", "yellow")
    
    # Запускаем фронтенд
    print_colored("\n5. Запуск фронтенда React...", "yellow")
    frontend_process = run_command("cd frontend && npm start", background=True)
    
    print_colored("\n=== ИНСТРУКЦИИ ===", "purple")
    print_colored("1. Система запущена и доступна через интернет", "green")
    print_colored("2. QR-коды для доступа сохранены в файлах:", "green")
    print_colored("   - api_qrcode.png     - для доступа к API", "green")
    print_colored("   - frontend_qrcode.png - для доступа к фронтенду", "green")
    print_colored("   - qrcodes.png        - оба QR-кода вместе", "green")
    print_colored("3. Добавьте эти QR-коды в вашу презентацию", "green")
    print_colored("4. Для остановки сервера закройте окна терминалов или нажмите Ctrl+C в них", "green")
    
    input("\nНажмите Enter для выхода из этого скрипта (серверы продолжат работать)...")

if __name__ == "__main__":
    main() 