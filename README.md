# Система подсчета количества студентов в аудитории

Проект представляет собой систему для подсчета количества студентов в аудитории с использованием компьютерного зрения (YOLO) и веб-интерфейса.

## Структура проекта

- `app/` - бэкенд на FastAPI
  - `api/v1/endpoints/` - API эндпоинты
  - `core/` - конфигурация и работа с БД
  - `ml/` - модели машинного обучения
  - `models/` - модели данных
  - `schemas/` - схемы Pydantic
- `frontend/` - фронтенд на React

## Требования

- Python 3.8+
- Node.js 14+
- MySQL 5.7+ или MariaDB 10.5+

## Установка и запуск

### База данных MySQL

1. Установите MySQL или используйте XAMPP:
   - MySQL: https://dev.mysql.com/downloads/installer/
   - XAMPP: https://www.apachefriends.org/download.html

2. Создайте базу данных с помощью скрипта:
```
python create_mysql_db.py
```

Или вручную через MySQL:
```sql
CREATE DATABASE attendance CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. При необходимости настройте подключение в файле `app/core/config.py`:
```python
DATABASE_URL = "mysql+pymysql://username:password@localhost/attendance"
```

### Бэкенд

1. Установите зависимости:
```
pip install -r requirements.txt
```

2. Запустите сервер:
```
uvicorn app.main:app --reload
```

Сервер будет доступен по адресу: http://localhost:8000

### Фронтенд

1. Перейдите в директорию frontend:
```
cd frontend
```

2. Установите зависимости:
```
npm install
```

3. Запустите фронтенд:
```
npm start
```

Фронтенд будет доступен по адресу: http://localhost:3000

## API эндпоинты

- `GET /api/v1/detect-live` - Запуск детекции с камеры
- `POST /api/v1/detect-image` - Детекция на загруженном изображении
- `GET /api/v1/attendance` - Получение истории посещаемости
- `POST /api/v1/attendance` - Добавление записи о посещаемости

## Работа с базой данных

Для управления базой данных MySQL рекомендуется использовать:
- phpMyAdmin (доступен через XAMPP)
- MySQL Workbench: https://dev.mysql.com/downloads/workbench/
- DBeaver: https://dbeaver.io/download/ (универсальный клиент для разных СУБД)

## Миграции базы данных

Для создания новой миграции:

```
alembic revision --autogenerate -m "описание изменений"
```

Для применения миграций:

```
alembic upgrade head
```

Для отката миграций:

```
alembic downgrade -1
```
