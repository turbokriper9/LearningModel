import os
import json
import shutil
import zipfile
import webbrowser
import time
import sys

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

def create_static_for_netlify():
    """Создает статические файлы для публикации на Netlify"""
    try:
        # Создаем директорию для статических файлов
        netlify_dir = "netlify_deploy"
        if os.path.exists(netlify_dir):
            shutil.rmtree(netlify_dir)
        os.makedirs(netlify_dir)
        
        # Проверяем наличие директории static_web_app
        if os.path.exists("static_web_app"):
            # Копируем содержимое static_web_app в netlify_dir
            for item in os.listdir("static_web_app"):
                src = os.path.join("static_web_app", item)
                dst = os.path.join(netlify_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            
            print_color("Файлы из static_web_app скопированы в netlify_deploy", "green")
        else:
            # Если директория static_web_app не существует, создаем все необходимые файлы
            print_color("Директория static_web_app не найдена, создаем необходимые файлы...", "yellow")
            
            # Здесь можно вызвать функции из create_frontend_app.py для создания статических файлов
            # Но для простоты просто создадим базовый HTML файл
            
            html_content = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Система учета посещаемости студентов</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            flex-direction: column;
            text-align: center;
        }
        
        .container {
            max-width: 800px;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }
        
        h1 {
            color: #4CAF50;
            margin-bottom: 20px;
        }
        
        p {
            line-height: 1.6;
            color: #555;
        }
        
        .button {
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 20px;
            font-weight: bold;
            transition: background-color 0.3s;
        }
        
        .button:hover {
            background-color: #3e8e41;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Система учета посещаемости студентов</h1>
        <p>
            Данная система разработана для автоматического подсчета количества студентов в аудитории 
            с использованием компьютерного зрения и искусственного интеллекта.
        </p>
        <p>
            Полный функционал системы доступен при локальном запуске приложения.
            Для демонстрационных целей этот сайт размещен на Netlify.
        </p>
        <p>
            <strong>Для создания полноценной версии сайта:</strong><br>
            Используйте скрипт create_frontend_app.py из исходного проекта.
        </p>
        <a href="https://github.com/your-username/your-repository" class="button">Открыть проект на GitHub</a>
    </div>
</body>
</html>
"""
            
            with open(os.path.join(netlify_dir, "index.html"), "w", encoding="utf-8") as f:
                f.write(html_content)
            
            print_color("Создан базовый HTML файл", "green")
        
        # Создаем файл netlify.toml для настройки деплоя
        netlify_toml = """[build]
  publish = "."
  
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
"""
        
        with open(os.path.join(netlify_dir, "netlify.toml"), "w", encoding="utf-8") as f:
            f.write(netlify_toml)
        
        # Создаем ZIP архив для удобной загрузки на Netlify
        zip_name = "netlify_deploy.zip"
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(netlify_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, netlify_dir))
        
        print_color(f"Архив {zip_name} успешно создан", "green")
        
        # Создаем инструкции по развертыванию на Netlify
        instructions = """# Инструкция по размещению на Netlify

## 1. Регистрация на Netlify

1. Перейдите на сайт [Netlify](https://app.netlify.com/signup) и зарегистрируйтесь
2. Можно зарегистрироваться через GitHub, GitLab, Bitbucket или по email

## 2. Размещение сайта на Netlify

### Вариант 1: Drag and Drop (самый простой)

1. После входа в аккаунт Netlify вы увидите страницу "Sites"
2. Перетащите ZIP-архив `netlify_deploy.zip` в область с надписью "Drag and drop your site folder here"
3. Подождите, пока файлы загрузятся и сайт будет опубликован

### Вариант 2: Через интерфейс загрузки

1. После входа в аккаунт Netlify нажмите "Add new site" -> "Deploy manually"
2. Распакуйте архив `netlify_deploy.zip` и перетащите содержимое в область загрузки
3. Подождите, пока файлы загрузятся и сайт будет опубликован

### Вариант 3: Через GitHub

1. Загрузите файлы из директории `netlify_deploy` в репозиторий на GitHub
2. В Netlify выберите "Add new site" -> "Import an existing project"
3. Выберите GitHub и предоставьте доступ к репозиториям
4. Выберите репозиторий с вашим сайтом
5. Оставьте настройки сборки по умолчанию и нажмите "Deploy site"

## 3. Настройка домена

1. После деплоя Netlify присвоит вашему сайту случайный поддомен (например, random-name-123456.netlify.app)
2. Вы можете изменить поддомен в настройках сайта:
   - Перейдите в раздел "Site settings" -> "Domain management"
   - Нажмите "Options" рядом с поддоменом Netlify и выберите "Edit site name"
   - Введите желаемое имя (например, attendance-system)
   - Ваш сайт будет доступен по адресу: https://attendance-system.netlify.app

## 4. Доступ к сайту

После публикации ваш сайт будет доступен по адресу:
```
https://ИМЯ-САЙТА.netlify.app
```

Этот URL можно преобразовать в QR-код для удобного доступа с помощью сервиса:
https://www.qr-code-generator.com/
"""
        
        with open(os.path.join(netlify_dir, "NETLIFY_DEPLOY_INSTRUCTIONS.md"), "w", encoding="utf-8") as f:
            f.write(instructions)
        
        print_color("Инструкции по размещению на Netlify созданы", "green")
        
        return {
            "dir": netlify_dir,
            "zip": zip_name
        }
    
    except Exception as e:
        print_color(f"Ошибка при создании файлов для Netlify: {e}", "red")
        return None

def main():
    print_color("\n=== ПОДГОТОВКА К РАЗМЕЩЕНИЮ НА NETLIFY ===\n", "cyan")
    
    # Шаг 1: Создание файлов для Netlify
    print_color("1. Создание файлов для публикации на Netlify...", "yellow")
    result = create_static_for_netlify()
    if not result:
        print_color("Не удалось создать файлы для Netlify. Прерывание операции.", "red")
        return
    
    # Шаг 2: Открытие директории с готовыми файлами
    print_color("\n2. Открытие директории с готовыми файлами...", "yellow")
    try:
        if sys.platform == 'win32':
            os.system(f'explorer "{os.path.abspath(result["dir"])}"')
        elif sys.platform == 'darwin':  # macOS
            os.system(f'open "{os.path.abspath(result["dir"])}"')
        else:  # Linux
            os.system(f'xdg-open "{os.path.abspath(result["dir"])}"')
    except Exception:
        print_color(f"Не удалось открыть директорию. Пожалуйста, откройте её вручную: {os.path.abspath(result['dir'])}", "red")
    
    # Шаг 3: Предложение открыть Netlify
    print_color("\n3. Открыть сайт Netlify для публикации? (y/n)", "yellow")
    open_netlify = input()
    if open_netlify.lower() == 'y':
        webbrowser.open("https://app.netlify.com/drop")
        print_color("\nПросто перетащите архив netlify_deploy.zip на открывшуюся страницу", "blue")
    
    # Шаг 4: Вывод инструкций
    print_color("\n=== ИНСТРУКЦИИ ===", "purple")
    print_color("1. Перетащите файл netlify_deploy.zip на страницу https://app.netlify.com/drop", "green")
    print_color("2. Netlify автоматически распакует архив и опубликует ваш сайт", "green")
    print_color("3. После публикации ваш сайт будет доступен по адресу:", "green")
    print_color("   https://случайное-имя.netlify.app", "cyan")
    print_color("4. Вы можете изменить случайное имя на своё в настройках сайта", "green")
    print_color("5. Подробные инструкции находятся в файле:", "green")
    print_color(f"   {os.path.abspath(os.path.join(result['dir'], 'NETLIFY_DEPLOY_INSTRUCTIONS.md'))}", "cyan")
    
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main() 