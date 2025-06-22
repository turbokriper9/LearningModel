from ultralytics import YOLO
import cv2
import numpy as np
import os
import time
import random
import traceback

print("Текущая директория:", os.getcwd())

# Проверяем наличие файла модели
model_paths = [
    "runs/detect/lasttrain/weights/headmodel.pt",  # Текущий путь
    "../runs/detect/lasttrain/weights/headmodel.pt",  # Относительный путь
    os.path.abspath("../runs/detect/lasttrain/weights/headmodel.pt"),  # Абсолютный путь
    "yolo_camera_project/runs/detect/lasttrain/weights/headmodel.pt",  # Альтернативный путь
    "../yolo_camera_project/runs/detect/lasttrain/weights/headmodel.pt",  # Другой альтернативный путь
    "yolo_camera_project/runs/detect/train2/weights/best.pt",  # Другая модель
    "yolo_camera_project/runs/detect/train4/weights/yolov11.pt",  # Еще одна модель
    "yolov8n.pt"  # Стандартная модель YOLOv8n (будет загружена автоматически)
]

# Проверяем все пути
for path in model_paths:
    print(f"Проверка пути {path}: {'Существует' if os.path.exists(path) else 'Не существует'}")

# Ищем первый доступный файл модели
model = None
for path in model_paths:
    if path == "yolov8n.pt" or os.path.exists(path):
        try:
            print(f"Загружаем модель из {path}")
            model = YOLO(path)
            print(f"Модель успешно загружена из {path}")
            
            # Если это стандартная модель YOLOv8n, выводим классы
            if path == "yolov8n.pt":
                print("Используется стандартная модель YOLOv8n")
                print("Доступные классы:", model.names)
                print("Класс 'person' имеет индекс:", list(model.names.keys())[list(model.names.values()).index('person')])
            
            break
        except Exception as e:
            print(f"Ошибка загрузки модели {path}: {str(e)}")

if model is None:
    print("ВНИМАНИЕ: Ни одна модель не найдена. Используется демо-режим.")

# Отключаем кэширование для более точных результатов
CACHE_ENABLED = False
last_result = None
last_detection_time = 0
CACHE_TIMEOUT = 0.1  # Уменьшаем кэширование до 100 мс

# Переменные для демо-режима
demo_last_update = 0
demo_update_interval = 2  # Обновляем демо-данные каждые 2 секунды
demo_count = 2

def get_demo_data():
    """
    Генерирует демо-данные с случайными вариациями
    """
    global demo_last_update, demo_count
    
    current_time = time.time()
    
    # Обновляем демо-данные каждые несколько секунд
    if current_time - demo_last_update > demo_update_interval:
        # Случайное изменение количества людей (-1, 0, +1)
        change = random.choice([-1, 0, 0, 1])
        demo_count = max(1, min(10, demo_count + change))  # Ограничиваем от 1 до 10
        demo_last_update = current_time
        
        print(f"Демо-режим: обновление количества людей до {demo_count}")
    
    # Генерируем случайные боксы
    boxes = []
    for i in range(demo_count):
        x1 = random.randint(50, 400)
        y1 = random.randint(50, 300)
        width = random.randint(50, 100)
        height = random.randint(100, 200)
        boxes.append({"xmin": x1, "ymin": y1, "xmax": x1 + width, "ymax": y1 + height})
    
    return {"count": demo_count, "boxes": boxes}

def detect_people_from_camera():
    """
    Обнаружение людей с камеры в реальном времени
    """
    try:
        # Если модель не загружена, возвращаем демо-данные с вариациями
        if model is None:
            print("Модель не загружена, используем демо-данные для камеры")
            return get_demo_data()
            
        cap = cv2.VideoCapture(0)
        success, frame = cap.read()
        cap.release()

        if not success:
            print("Ошибка: Не удалось получить кадр с камеры")
            return {"count": 0, "boxes": []}

        print(f"Запуск детекции на кадре с камеры размером {frame.shape}")
        results = model(frame)
        
        # Получаем информацию о модели
        model_type = str(model.ckpt_path)
        print(f"Используемая модель для камеры: {model_type}")
        
        # Для отладки выводим все обнаруженные объекты
        all_boxes = results[0].boxes
        print(f"Всего обнаружено объектов на кадре: {len(all_boxes)}")
        
        count = 0
        boxes = []
        
        for box in results[0].boxes:
            # Получаем класс объекта и уверенность
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            
            # Выводим информацию о каждом объекте
            print(f"Обнаружен объект на кадре: класс={cls_id}, уверенность={conf:.2f}")
            
            # Для стандартной модели YOLOv8n фильтруем только людей (класс 0)
            if "yolov8n.pt" in model_type:
                if cls_id == 0 and conf > 0.3:  # 0 - класс person в COCO
                    count += 1
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    boxes.append({"xmin": x1, "ymin": y1, "xmax": x2, "ymax": y2})
                    print(f"  - Добавлен человек: {x1},{y1} - {x2},{y2}")
            else:
                # Для специализированной модели берем все обнаруженные объекты с достаточной уверенностью
                if conf > 0.3:  # Минимальный порог уверенности
                    count += 1
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    boxes.append({"xmin": x1, "ymin": y1, "xmax": x2, "ymax": y2})
                    print(f"  - Добавлен объект: {x1},{y1} - {x2},{y2}")
        
        print(f"Итого обнаружено людей на кадре: {count}")
        return {"count": count, "boxes": boxes}
    except Exception as e:
        print(f"Ошибка при обнаружении людей с камеры: {str(e)}")
        traceback.print_exc()
        return {"count": 0, "boxes": []}

def detect_people_from_image(img):
    """
    Обнаружение людей на загруженном изображении
    
    Args:
        img: Изображение в формате numpy array (BGR)
        
    Returns:
        dict: Словарь с количеством обнаруженных людей и координатами рамок
    """
    global last_result, last_detection_time
    
    try:
        current_time = time.time()
        
        # Используем кэшированный результат только если включено кэширование
        if CACHE_ENABLED and last_result and (current_time - last_detection_time) < CACHE_TIMEOUT:
            return last_result
            
        if img is None:
            print("Изображение пустое")
            return {"count": 0, "boxes": []}
            
        # Если модель не загружена, возвращаем демо-данные с вариациями
        if model is None:
            print("Модель не загружена, используем демо-данные")
            result = get_demo_data()
            
            # Кэшируем результат
            if CACHE_ENABLED:
                last_result = result
                last_detection_time = current_time
                
            return result
        
        # Для отладки сохраняем последнее изображение (раз в 10 секунд)
        if current_time % 10 < 0.5:
            debug_path = "debug_latest.jpg"
            cv2.imwrite(debug_path, img)
            print(f"Сохранено отладочное изображение: {debug_path}, размер: {img.shape}")
            
        # Запускаем детекцию с оптимизированными параметрами
        print(f"Запуск детекции на изображении размером {img.shape}")
        results = model(img, verbose=False)
        
        # Получаем информацию о модели
        model_type = str(model.ckpt_path)
        print(f"Используемая модель: {model_type}")
        
        # Для отладки выводим все обнаруженные объекты
        all_boxes = results[0].boxes
        print(f"Всего обнаружено объектов: {len(all_boxes)}")
        
        count = 0
        boxes = []
        
        for box in results[0].boxes:
            # Получаем класс объекта и уверенность
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            
            # Выводим информацию о каждом объекте
            print(f"Обнаружен объект: класс={cls_id}, уверенность={conf:.2f}")
            
            # Для стандартной модели YOLOv8n фильтруем только людей (класс 0)
            if "yolov8n.pt" in model_type:
                if cls_id == 0 and conf > 0.3:  # 0 - класс person в COCO
                    count += 1
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    boxes.append({"xmin": x1, "ymin": y1, "xmax": x2, "ymax": y2})
                    print(f"  - Добавлен человек: {x1},{y1} - {x2},{y2}")
            else:
                # Для специализированной модели берем все обнаруженные объекты с достаточной уверенностью
                if conf > 0.3:  # Минимальный порог уверенности
                    count += 1
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    boxes.append({"xmin": x1, "ymin": y1, "xmax": x2, "ymax": y2})
                    print(f"  - Добавлен объект: {x1},{y1} - {x2},{y2}")
        
        print(f"Итого обнаружено людей: {count}")
        result = {"count": count, "boxes": boxes}
        
        # Кэшируем результат только если включено кэширование
        if CACHE_ENABLED:
            last_result = result
            last_detection_time = current_time
        
        return result
    except Exception as e:
        print(f"Ошибка при обнаружении людей на изображении: {str(e)}")
        traceback.print_exc()
        return {"count": 0, "boxes": []}