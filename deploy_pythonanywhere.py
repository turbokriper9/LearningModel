import os
import sys
import zipfile
import webbrowser
import time

def print_color(text, color):
    """Печать цветного текста"""
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

def create_zip_archive():
    """Создает ZIP-архив с необходимыми файлами проекта"""
    try:
        # Имя архива
        zip_name = "attendance_app.zip"
        
        # Файлы и директории для архивации
        files_to_zip = [
            "app/",
            "requirements.txt",
            "README.md"
        ]
        
        # Создаем архив
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for item in files_to_zip:
                if os.path.isdir(item):
                    # Если это директория, добавляем все файлы из нее
                    for root, dirs, files in os.walk(item):
                        for file in files:
                            file_path = os.path.join(root, file)
                            # Исключаем кэши Python и виртуальные окружения
                            if '__pycache__' not in file_path and '.pyc' not in file_path:
                                zipf.write(file_path)
                elif os.path.isfile(item):
                    # Если это файл, добавляем его напрямую
                    zipf.write(item)
        
        print_color(f"Архив {zip_name} успешно создан", "green")
        return zip_name
    except Exception as e:
        print_color(f"Ошибка при создании архива: {e}", "red")
        return None

def create_pythonanywhere_instructions(zip_name):
    """Создает файл с инструкциями по развертыванию на PythonAnywhere"""
    instructions = f"""# Инструкция по размещению приложения на PythonAnywhere

## 1. Регистрация на PythonAnywhere

1. Перейдите на сайт [PythonAnywhere](https://www.pythonanywhere.com/) и зарегистрируйтесь
2. Даже бесплатный аккаунт подойдет для демонстрации проекта

## 2. Загрузка архива

1. В панели PythonAnywhere перейдите во вкладку "Files"
2. Нажмите кнопку "Upload a file" и загрузите файл `{zip_name}` из этой директории

## 3. Распаковка архива

1. Перейдите во вкладку "Consoles" и откройте Bash консоль
2. Выполните следующие команды:
```
cd
unzip {zip_name} -d attendance_app
cd attendance_app
```

## 4. Установка зависимостей

1. В той же консоли установите необходимые пакеты:
```
pip install --user -r requirements.txt
pip install --user uvicorn
```

## 5. Настройка веб-приложения

1. Перейдите во вкладку "Web"
2. Нажмите кнопку "Add a new web app"
3. Выберите "Manual configuration" и Python 3.9 (или новее)
4. Введите путь к вашему проекту: `/home/YOUR_USERNAME/attendance_app`
5. В разделе "Code" найдите "WSGI configuration file" и нажмите на ссылку
6. Замените все содержимое файла на следующий код:

```python
import sys
import os

path = '/home/YOUR_USERNAME/attendance_app'
if path not in sys.path:
    sys.path.append(path)

from app.main import app

application = app
```

7. Сохраните файл
8. Вернитесь на страницу настроек Web-приложения
9. В разделе "Virtualenv" введите `/home/YOUR_USERNAME/.virtualenvs/myenv`
10. Нажмите "Reload" для перезапуска приложения

## 6. Доступ к приложению

После выполнения всех шагов ваше приложение будет доступно по адресу:
```
https://YOUR_USERNAME.pythonanywhere.com
```

Этот URL можно преобразовать в QR-код для удобного доступа.

## Дополнительно: Настройка базы данных

Если ваше приложение использует базу данных, вам нужно будет создать ее на PythonAnywhere:

1. Перейдите во вкладку "Databases"
2. Инициализируйте базу данных SQLite или MySQL (в зависимости от вашего приложения)
3. Обновите настройки подключения к базе данных в приложении
"""
    
    # Записываем инструкции в файл
    with open("pythonanywhere_deploy_instructions.md", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print_color("Инструкции по развертыванию созданы в файле pythonanywhere_deploy_instructions.md", "green")
    return "pythonanywhere_deploy_instructions.md"

def main():
    print_color("\n=== ПОДГОТОВКА К РАЗМЕЩЕНИЮ ПРИЛОЖЕНИЯ В ИНТЕРНЕТЕ ===\n", "cyan")
    
    # Шаг 1: Создание архива
    print_color("1. Создание архива с приложением...", "yellow")
    zip_name = create_zip_archive()
    if not zip_name:
        print_color("Не удалось создать архив. Прерывание операции.", "red")
        return
    
    # Шаг 2: Создание инструкций
    print_color("\n2. Создание инструкций по развертыванию...", "yellow")
    instructions_file = create_pythonanywhere_instructions(zip_name)
    
    # Шаг 3: Открытие сайта для регистрации
    print_color("\n3. Открытие сайта PythonAnywhere...", "yellow")
    print_color("   Сейчас в браузере откроется сайт для регистрации.", "blue")
    
    try:
        time.sleep(2)
        webbrowser.open("https://www.pythonanywhere.com/registration/register/beginner/")
    except Exception:
        print_color("   Не удалось автоматически открыть браузер.", "red")
        print_color("   Пожалуйста, откройте https://www.pythonanywhere.com/registration/register/beginner/ вручную", "yellow")
    
    # Шаг 4: Вывод инструкций
    print_color("\n=== ИНСТРУКЦИИ ===", "purple")
    print_color("1. Зарегистрируйтесь на PythonAnywhere (бесплатный аккаунт)", "green")
    print_color("2. Следуйте инструкциям в файле:", "green")
    print_color(f"   {instructions_file}", "green")
    print_color("3. После развертывания ваше приложение будет доступно по адресу:", "green")
    print_color("   https://ВАШ_ЛОГИН.pythonanywhere.com", "cyan")
    print_color("4. Вы можете создать QR-код для этого адреса онлайн:", "green")
    print_color("   https://www.qr-code-generator.com/", "cyan")
    
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main() 