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
            
            # Выводим информацию о классах модели
            print("Доступные классы в модели:", model.names)
            if path == "yolov8n.pt":
                print("Используется стандартная модель YOLOv8n")
                if 'person' in model.names.values():
                    print("Класс 'person' имеет индекс:", list(model.names.keys())[list(model.names.values()).index('person')])
            else:
                print("Используется специализированная модель")
            
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

# Функция для получения списка доступных камер
def get_available_cameras(max_cameras=10):
    """
    Проверяет доступные камеры в системе
    
    Args:
        max_cameras: Максимальное количество камер для проверки
        
    Returns:
        list: Список доступных индексов камер
    """
    available_cameras = []
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cameras.append(i)
            cap.release()
        else:
            cap.release()
    
    print(f"Доступные камеры: {available_cameras}")
    return available_cameras

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

def detect_people_from_camera(camera_id=0):
    """
    Обнаружение людей с камеры в реальном времени
    
    Args:
        camera_id: Индекс камеры (0 - встроенная камера, 1+ - внешние камеры)
        
    Returns:
        dict: Словарь с количеством обнаруженных людей и координатами рамок
    """
    try:
        # Если модель не загружена, возвращаем демо-данные с вариациями
        if model is None:
            print("Модель не загружена, используем демо-данные для камеры")
            return get_demo_data()
        
        print(f"Пытаемся открыть камеру с индексом {camera_id}")
        
        # Пробуем несколько раз открыть камеру для большей надежности
        max_attempts = 3
        cap = None
        
        for attempt in range(max_attempts):
            try:
                cap = cv2.VideoCapture(camera_id)
                if cap.isOpened():
                    print(f"Камера {camera_id} успешно открыта (попытка {attempt+1})")
                    break
                else:
                    print(f"Не удалось открыть камеру {camera_id} (попытка {attempt+1})")
                    if cap:
                        cap.release()
                    time.sleep(0.5)  # Небольшая пауза перед следующей попыткой
            except Exception as e:
                print(f"Ошибка при попытке открыть камеру {camera_id}: {str(e)}")
                if cap:
                    cap.release()
                time.sleep(0.5)
        
        # Если не удалось открыть камеру после всех попыток
        if cap is None or not cap.isOpened():
            print(f"Ошибка: Не удалось открыть камеру с индексом {camera_id} после {max_attempts} попыток")
            # Пробуем открыть камеру с индексом 0 в качестве запасного варианта
            if camera_id != 0:
                print("Пробуем открыть камеру с индексом 0")
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    print("Ошибка: Не удалось открыть камеру с индексом 0")
                    return {"count": 0, "boxes": [], "error": f"Не удалось открыть камеру {camera_id}", "camera_id": camera_id}
            else:
                return {"count": 0, "boxes": [], "error": "Не удалось открыть камеру", "camera_id": camera_id}
        
        # Получаем информацию о камере
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(f"Камера {camera_id}: разрешение {width}x{height}, FPS: {fps}")
        
        # Читаем кадр
        success, frame = cap.read()
        cap.release()

        if not success:
            print(f"Ошибка: Не удалось получить кадр с камеры {camera_id}")
            return {"count": 0, "boxes": [], "error": f"Не удалось получить кадр с камеры {camera_id}", "camera_id": camera_id}

        print(f"Запуск детекции на кадре с камеры {camera_id} размером {frame.shape}")
        
        # Для отладки сохраняем кадр
        debug_path = f"debug_frames/camera_{camera_id}_frame.jpg"
        os.makedirs("debug_frames", exist_ok=True)
        cv2.imwrite(debug_path, frame)
        print(f"Сохранено отладочное изображение: {debug_path}")

        results = model(frame)
        
        # Получаем информацию о модели
        model_type = str(model.ckpt_path)
        print(f"Используемая модель для камеры: {model_type}")
        
        # Для отладки выводим все обнаруженные объекты
        all_boxes = results[0].boxes
        print(f"Всего обнаружено объектов на кадре: {len(all_boxes)}")
        
        count = 0
        boxes = []
        
        # Принимаем ВСЕ обнаруженные объекты с минимальным порогом уверенности
        for box in results[0].boxes:
            # Получаем класс объекта и уверенность
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            
            # Выводим информацию о каждом объекте
            print(f"Обнаружен объект на кадре: класс={cls_id}, уверенность={conf:.2f}")
            
            # Используем крайне низкий порог уверенности для всех классов
            if conf > 0.1:  # Критически снижаем порог до 0.1, чтобы максимизировать количество детекций
                count += 1
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                boxes.append({"xmin": x1, "ymin": y1, "xmax": x2, "ymax": y2})
                print(f"  - Добавлен объект: класс={cls_id}, координаты={x1},{y1} - {x2},{y2}")
            else:
                print(f"  - Объект отклонен из-за низкой уверенности: {conf:.2f} < 0.1")
        
        print(f"Итого обнаружено объектов на кадре: {count}")
        return {"count": count, "boxes": boxes, "camera_id": camera_id}
    except Exception as e:
        print(f"Ошибка при обнаружении объектов с камеры {camera_id}: {str(e)}")
        traceback.print_exc()
        return {"count": 0, "boxes": [], "error": str(e), "camera_id": camera_id}

def detect_people_from_image(img):
    """
    Обнаружение объектов на загруженном изображении
    
    Args:
        img: Изображение в формате numpy array (BGR)
        
    Returns:
        dict: Словарь с количеством обнаруженных объектов и координатами рамок
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
        
        # Принимаем ВСЕ обнаруженные объекты с минимальным порогом уверенности
        for box in results[0].boxes:
            # Получаем класс объекта и уверенность
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            
            # Выводим информацию о каждом объекте
            print(f"Обнаружен объект: класс={cls_id}, уверенность={conf:.2f}")
            
            # Используем крайне низкий порог уверенности для всех классов
            if conf > 0.1:  # Критически снижаем порог до 0.1, чтобы максимизировать количество детекций
                count += 1
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                boxes.append({"xmin": x1, "ymin": y1, "xmax": x2, "ymax": y2})
                print(f"  - Добавлен объект: класс={cls_id}, координаты={x1},{y1} - {x2},{y2}")
            else:
                print(f"  - Объект отклонен из-за низкой уверенности: {conf:.2f} < 0.1")
        
        print(f"Итого обнаружено объектов: {count}")
        result = {"count": count, "boxes": boxes}
        
        # Кэшируем результат только если включено кэширование
        if CACHE_ENABLED:
            last_result = result
            last_detection_time = current_time
        
        return result
    except Exception as e:
        print(f"Ошибка при обнаружении объектов на изображении: {str(e)}")
        traceback.print_exc()
        return {"count": 0, "boxes": []}