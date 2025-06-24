import os
import json
import shutil
import subprocess
import sys
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

def create_static_app():
    """Создает статическое веб-приложение на основе существующего фронтенда"""
    try:
        # Проверяем, существует ли директория frontend
        if not os.path.exists("frontend"):
            print_color("Ошибка: Директория frontend не найдена", "red")
            return False

        # Создаем директорию для статического приложения
        static_app_dir = "static_web_app"
        if os.path.exists(static_app_dir):
            shutil.rmtree(static_app_dir)
        os.makedirs(static_app_dir)
        
        # Создаем директорию public и копируем в нее статические файлы
        public_dir = os.path.join(static_app_dir, "public")
        os.makedirs(public_dir)
        
        if os.path.exists("frontend/public"):
            for item in os.listdir("frontend/public"):
                src = os.path.join("frontend/public", item)
                dst = os.path.join(public_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
        
        # Создаем базовый HTML файл
        html_content = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Система учета посещаемости студентов</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="app">
        <header>
            <h1>
                <img src="public/images/URFU.png" alt="УрФУ" class="logo">
                Система подсчета студентов
            </h1>
            <div class="tabs">
                <button class="active" onclick="showTab('main')">Камера</button>
                <button onclick="showTab('stats')">Статистика</button>
            </div>
        </header>

        <main>
            <div id="main-tab" class="tab-content">
                <div class="camera-container">
                    <div class="video-wrapper">
                        <div class="camera-placeholder">
                            <p>Для работы с камерой посетите приложение локально</p>
                            <p>Это демонстрационная версия системы</p>
                        </div>
                    </div>
                    
                    <div class="detection-info">
                        <div class="count">
                            <span class="count-number" id="counter">25</span>
                            <span class="count-label">студентов</span>
                            <div class="save-info">
                                <span class="save-status success">
                                    Демонстрационный режим
                                </span>
                                <span class="save-hint">
                                    Данные обновляются каждые 5 секунд
                                </span>
                                <button class="manual-save-btn" onclick="updateDemoCount()">
                                    Обновить данные
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div id="stats-tab" class="tab-content" style="display: none;">
                <div class="stats-filters">
                    <div class="filter-item">
                        <label for="date-filter">Дата:</label>
                        <input type="date" id="date-filter" value="2025-06-24">
                    </div>
                    
                    <div class="filter-item">
                        <label for="lesson-filter">Пара:</label>
                        <select id="lesson-filter">
                            <option value="">Все пары (общая статистика)</option>
                            <option value="1">1 пара (8:30-10:00)</option>
                            <option value="2">2 пара (10:15-11:45)</option>
                            <option value="3">3 пара (12:00-13:30)</option>
                            <option value="4">4 пара (14:15-15:45)</option>
                            <option value="5">5 пара (16:00-17:30)</option>
                            <option value="6">6 пара (17:40-19:10)</option>
                            <option value="7">7 пара (19:15-20:45)</option>
                            <option value="8">8 пара (20:50-22:20)</option>
                        </select>
                    </div>
                </div>
                
                <div class="chart-container">
                    <h2>Демонстрационные данные посещаемости</h2>
                    <div class="demo-chart">
                        <div class="demo-bar" style="height: 80px;">
                            <div class="demo-label">1 пара</div>
                            <div class="demo-value">18</div>
                        </div>
                        <div class="demo-bar" style="height: 100px;">
                            <div class="demo-label">2 пара</div>
                            <div class="demo-value">22</div>
                        </div>
                        <div class="demo-bar" style="height: 120px;">
                            <div class="demo-label">3 пара</div>
                            <div class="demo-value">25</div>
                        </div>
                        <div class="demo-bar" style="height: 110px;">
                            <div class="demo-label">4 пара</div>
                            <div class="demo-value">23</div>
                        </div>
                        <div class="demo-bar" style="height: 90px;">
                            <div class="demo-label">5 пара</div>
                            <div class="demo-value">20</div>
                        </div>
                        <div class="demo-bar" style="height: 70px;">
                            <div class="demo-label">6 пара</div>
                            <div class="demo-value">15</div>
                        </div>
                    </div>
                </div>
                
                <div class="info-container">
                    <h2>О системе учета посещаемости</h2>
                    <p>
                        Данная система разработана для автоматического подсчета количества студентов в аудитории 
                        с использованием компьютерного зрения и искусственного интеллекта.
                    </p>
                    <p>
                        Основные возможности системы:
                    </p>
                    <ul>
                        <li>Автоматическое определение количества студентов в аудитории через камеру</li>
                        <li>Привязка статистики к конкретным парам и дням недели</li>
                        <li>Построение графиков посещаемости</li>
                        <li>Экспорт статистики</li>
                    </ul>
                    <p>
                        Для полного доступа ко всем функциям системы, включая работу с камерой, 
                        необходимо запустить систему локально.
                    </p>
                </div>
            </div>
        </main>
    </div>

    <script src="app.js"></script>
</body>
</html>
"""
        
        with open(os.path.join(static_app_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # Создаем простой JavaScript файл
        js_content = """// Демонстрационный скрипт для статической версии приложения
function showTab(tabName) {
    // Скрываем все вкладки
    const tabs = document.getElementsByClassName('tab-content');
    for (let i = 0; i < tabs.length; i++) {
        tabs[i].style.display = 'none';
    }
    
    // Показываем выбранную вкладку
    document.getElementById(tabName + '-tab').style.display = 'block';
    
    // Обновляем активную кнопку
    const buttons = document.querySelector('.tabs').getElementsByTagName('button');
    for (let i = 0; i < buttons.length; i++) {
        if (buttons[i].onclick.toString().includes(tabName)) {
            buttons[i].classList.add('active');
        } else {
            buttons[i].classList.remove('active');
        }
    }
}

// Функция для демонстрационного обновления счетчика
function updateDemoCount() {
    // Генерируем случайное число от 15 до 30
    const randomCount = Math.floor(Math.random() * 16) + 15;
    
    // Обновляем счетчик
    const counter = document.getElementById('counter');
    counter.textContent = randomCount;
    
    // Обновляем подпись
    const label = counter.nextElementSibling;
    if (randomCount === 1) {
        label.textContent = 'студент';
    } else if (randomCount >= 2 && randomCount <= 4) {
        label.textContent = 'студента';
    } else {
        label.textContent = 'студентов';
    }
    
    // Добавляем анимацию
    counter.classList.add('updated');
    setTimeout(() => {
        counter.classList.remove('updated');
    }, 500);
}

// Автоматическое обновление счетчика каждые 10 секунд
setInterval(updateDemoCount, 10000);

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    updateDemoCount();
});
"""
        
        with open(os.path.join(static_app_dir, "app.js"), "w", encoding="utf-8") as f:
            f.write(js_content)
        
        # Создаем CSS файл на основе стилей из App.js
        css_content = """body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
}

.app {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    color: #333;
}

header {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 20px;
}

h1 {
    display: flex;
    align-items: center;
    font-size: 28px;
    margin-bottom: 20px;
}

.logo {
    height: 40px;
    margin-right: 15px;
}

.tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.tabs button {
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    background-color: #eee;
    cursor: pointer;
    font-size: 16px;
    transition: all 0.3s;
}

.tabs button.active {
    background-color: #4CAF50;
    color: white;
}

.camera-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
}

.video-wrapper {
    position: relative;
    width: 100%;
    max-width: 800px;
    margin-bottom: 20px;
    aspect-ratio: 16/9;
    background-color: #000;
    border-radius: 8px;
    overflow: hidden;
}

.camera-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
    color: #fff;
    font-size: 18px;
    text-align: center;
    background-color: #333;
}

.detection-info {
    margin-top: 20px;
    text-align: center;
}

.count {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-height: 200px;
    background-color: #f8f8f8;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    margin-top: 20px;
    width: 100%;
    max-width: 400px;
    margin: 0 auto;
}

.count-number {
    font-size: 72px;
    font-weight: bold;
    color: #4CAF50;
    transition: all 0.5s ease-in-out;
    min-width: 150px;
    min-height: 90px;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 10px 0;
    border-radius: 20px;
    background-color: rgba(76, 175, 80, 0.1);
    padding: 15px 25px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.count-number.updated {
    animation: fadeNumber 0.5s ease-out;
}

@keyframes fadeNumber {
    from { opacity: 0.5; transform: scale(0.95); }
    to { opacity: 1; transform: scale(1); }
}

.count-label {
    font-size: 28px;
    color: #666;
    margin-bottom: 20px;
    transition: color 0.5s ease-in-out;
    min-width: 180px;
    min-height: 40px;
    text-align: center;
    display: flex;
    align-items: center;
    justify-content: center;
}

.save-info {
    margin-top: 15px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    background-color: #f9f9f9;
    padding: 15px;
    border-radius: 10px;
    width: 100%;
    max-width: 300px;
    border: 1px solid #eee;
}

.save-status {
    font-size: 14px;
    font-weight: 500;
    transition: opacity 0.3s ease;
}

.save-status.success {
    color: #2e7d32;
}

.save-status.error {
    color: #d32f2f;
}

.save-hint {
    font-size: 12px;
    color: #757575;
    font-style: italic;
    margin-bottom: 8px;
}

.manual-save-btn {
    padding: 6px 12px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s;
}

.manual-save-btn:hover {
    background-color: #3e8e41;
}

.stats-filters {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
    background-color: #f5f5f5;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.filter-item {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.filter-item label {
    font-weight: bold;
    font-size: 14px;
}

.filter-item input, .filter-item select {
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background-color: white;
}

.chart-container, .info-container {
    background-color: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
}

.demo-chart {
    display: flex;
    justify-content: space-around;
    align-items: flex-end;
    height: 300px;
    margin-top: 30px;
}

.demo-bar {
    width: 60px;
    background-color: #4CAF50;
    border-radius: 5px 5px 0 0;
    position: relative;
    transition: height 0.5s ease;
}

.demo-label {
    position: absolute;
    bottom: -25px;
    left: 0;
    width: 100%;
    text-align: center;
    font-size: 14px;
}

.demo-value {
    position: absolute;
    top: -25px;
    left: 0;
    width: 100%;
    text-align: center;
    font-weight: bold;
    color: #333;
}

.info-container h2 {
    color: #4CAF50;
    margin-top: 0;
}

.info-container ul {
    padding-left: 20px;
}

.info-container li {
    margin-bottom: 10px;
}

/* Адаптивный дизайн */
@media (max-width: 768px) {
    .demo-chart {
        height: 200px;
    }
    
    .demo-bar {
        width: 40px;
    }
    
    .count-number {
        font-size: 48px;
        min-height: 60px;
    }
    
    .count-label {
        font-size: 20px;
    }
}
"""
        
        with open(os.path.join(static_app_dir, "styles.css"), "w", encoding="utf-8") as f:
            f.write(css_content)
        
        # Создаем директорию для изображений
        images_dir = os.path.join(public_dir, "images")
        os.makedirs(images_dir, exist_ok=True)
        
        # Копируем логотип, если существует
        logo_paths = [
            "frontend/public/images/URFU.png",
            "images/URFU.png",
            "frontend/src/images/URFU.png"
        ]
        
        logo_copied = False
        for logo_path in logo_paths:
            if os.path.exists(logo_path):
                shutil.copy2(logo_path, os.path.join(images_dir, "URFU.png"))
                logo_copied = True
                break
        
        if not logo_copied:
            print_color("Предупреждение: Логотип УРФУ не найден", "yellow")
        
        # Создаем README файл с инструкциями
        readme_content = """# Демонстрационная версия системы учета посещаемости

Это статическая демонстрационная версия системы учета посещаемости студентов.
Данная версия предназначена только для демонстрации интерфейса и не содержит полной функциональности.

## Размещение на GitHub Pages

1. Создайте репозиторий на GitHub
2. Загрузите все файлы из этой директории в репозиторий
3. В настройках репозитория (Settings -> Pages) включите GitHub Pages
4. Выберите ветку main и директорию / (root) для публикации
5. Сохраните настройки

Через несколько минут ваш сайт будет доступен по адресу:
https://ВАШ_ЛОГИН.github.io/ИМЯ_РЕПОЗИТОРИЯ/

## Размещение на другом хостинге

Вы можете разместить эти файлы на любом статическом хостинге, например:
- Netlify
- Vercel
- Surge
- Cloudflare Pages

## Полная версия системы

Для доступа к полной версии системы с работающей камерой и распознаванием
необходимо запустить приложение локально.
"""
        
        with open(os.path.join(static_app_dir, "README.md"), "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        print_color(f"Статическое веб-приложение успешно создано в директории {static_app_dir}", "green")
        return static_app_dir
    
    except Exception as e:
        print_color(f"Ошибка при создании статического веб-приложения: {e}", "red")
        return None

def create_github_instructions(app_dir):
    """Создает инструкции по размещению на GitHub Pages"""
    instructions = """# Инструкция по размещению на GitHub Pages

## 1. Создание репозитория на GitHub

1. Перейдите на сайт [GitHub](https://github.com/) и войдите в свой аккаунт
2. Нажмите "+" в правом верхнем углу и выберите "New repository"
3. Укажите имя репозитория, например "attendance-system"
4. Сделайте репозиторий публичным (Public)
5. Нажмите "Create repository"

## 2. Загрузка файлов в репозиторий

### Вариант 1: Через GitHub Desktop

1. Установите [GitHub Desktop](https://desktop.github.com/)
2. Войдите в свой аккаунт GitHub
3. Клонируйте созданный репозиторий
4. Скопируйте все файлы из директории "static_web_app" в директорию репозитория
5. Сделайте коммит и нажмите "Push to origin"

### Вариант 2: Через веб-интерфейс GitHub

1. Перейдите в созданный репозиторий на GitHub
2. Нажмите "Add file" -> "Upload files"
3. Перетащите все файлы из директории "static_web_app" в область загрузки
4. Нажмите "Commit changes"

## 3. Настройка GitHub Pages

1. Перейдите на страницу вашего репозитория на GitHub
2. Нажмите "Settings" -> "Pages" (в левой боковой панели)
3. В разделе "Source" выберите ветку "main" и папку "/" (root)
4. Нажмите "Save"
5. Подождите несколько минут, пока сайт будет опубликован

## 4. Доступ к сайту

После публикации ваш сайт будет доступен по адресу:
```
https://ВАШ_ЛОГИН.github.io/ИМЯ_РЕПОЗИТОРИЯ/
```

Например, если ваш логин на GitHub - "user123", а имя репозитория - "attendance-system", 
то адрес будет:
```
https://user123.github.io/attendance-system/
```

Этот URL можно преобразовать в QR-код с помощью сервиса:
https://www.qr-code-generator.com/
"""
    
    # Записываем инструкции в файл
    instructions_file = os.path.join(app_dir, "GITHUB_DEPLOY.md")
    with open(instructions_file, "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print_color(f"Инструкции по размещению на GitHub Pages созданы в файле {instructions_file}", "green")
    return instructions_file

def main():
    print_color("\n=== СОЗДАНИЕ ДЕМОНСТРАЦИОННОЙ ВЕРСИИ САЙТА ===\n", "cyan")
    
    # Шаг 1: Создание статического приложения
    print_color("1. Создание статического веб-приложения...", "yellow")
    app_dir = create_static_app()
    if not app_dir:
        print_color("Не удалось создать статическое веб-приложение. Прерывание операции.", "red")
        return
    
    # Шаг 2: Создание инструкций
    print_color("\n2. Создание инструкций по размещению на GitHub Pages...", "yellow")
    instructions_file = create_github_instructions(app_dir)
    
    # Шаг 3: Открытие директории с готовым приложением
    print_color("\n3. Открытие директории с готовым приложением...", "yellow")
    try:
        if sys.platform == 'win32':
            os.system(f'explorer "{os.path.abspath(app_dir)}"')
        elif sys.platform == 'darwin':  # macOS
            os.system(f'open "{os.path.abspath(app_dir)}"')
        else:  # Linux
            os.system(f'xdg-open "{os.path.abspath(app_dir)}"')
    except Exception:
        print_color(f"Не удалось открыть директорию. Пожалуйста, откройте её вручную: {os.path.abspath(app_dir)}", "red")
    
    # Шаг 4: Вывод инструкций
    print_color("\n=== ИНСТРУКЦИИ ===", "purple")
    print_color("1. Загрузите файлы из директории static_web_app на GitHub", "green")
    print_color("2. Следуйте инструкциям в файле GITHUB_DEPLOY.md", "green")
    print_color("3. После публикации ваш сайт будет доступен по адресу:", "green")
    print_color("   https://ВАШ_ЛОГИН.github.io/ИМЯ_РЕПОЗИТОРИЯ/", "cyan")
    print_color("4. Этот адрес можно преобразовать в QR-код для удобного доступа", "green")
    
    # Шаг 5: Предложение открыть GitHub
    print_color("\n4. Перейти на GitHub для создания репозитория? (y/n)", "yellow")
    open_github = input()
    if open_github.lower() == 'y':
        webbrowser.open("https://github.com/new")
    
    input("\nНажмите Enter для выхода...")

if __name__ == "__main__":
    main() 