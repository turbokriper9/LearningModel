# Инструкция по размещению приложения на PythonAnywhere

## 1. Регистрация на PythonAnywhere

1. Перейдите на сайт [PythonAnywhere](https://www.pythonanywhere.com/) и зарегистрируйтесь
2. Даже бесплатный аккаунт подойдет для демонстрации проекта

## 2. Загрузка архива

1. В панели PythonAnywhere перейдите во вкладку "Files"
2. Нажмите кнопку "Upload a file" и загрузите файл `attendance_app.zip` из этой директории

## 3. Распаковка архива

1. Перейдите во вкладку "Consoles" и откройте Bash консоль
2. Выполните следующие команды:
```
cd
unzip attendance_app.zip -d attendance_app
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
