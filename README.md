# Разработка системы подсчета количества студентов в аудиториях

Инструкция по запуску проекта

1. Клонируйте проект
git clone https://github.com/turbokriper9/LearningModel.git
cd LearningModel

2. Установите зависимости Python

Рекомендуется использовать виртуальное окружение:
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

3. Установите зависимости для фронтенда
cd frontend
npm install
cd ..

4. Скачайте весовые файлы YOLOv8
4.1. Скачайте файл по ссылке:
Скачать best.pt с Яндекс Диска по ссылке: https://disk.yandex.ru/d/0nqOc4HNfMBTSQ
4.2. Положите его по пути: runs/detect/train2/weights/best.pt

Если этих папок нет, создайте их: mkdir -p runs/detect/train2/weights

Убедитесь, что путь в коде совпадает: model = YOLO("runs/detect/train2/weights/best.pt")
