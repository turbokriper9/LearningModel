import cv2
import numpy as np
import time
import os

def list_available_cameras(max_cameras=10):
    """
    Проверяет доступные камеры в системе
    
    Args:
        max_cameras: Максимальное количество камер для проверки
        
    Returns:
        list: Список доступных индексов камер
    """
    available_cameras = []
    for i in range(max_cameras):
        try:
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)  # Используем DirectShow для Windows
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    available_cameras.append(i)
                    print(f"Камера {i} доступна")
                cap.release()
            else:
                print(f"Камера {i} недоступна")
        except Exception as e:
            print(f"Ошибка при проверке камеры {i}: {str(e)}")
    
    return available_cameras

def test_cameras():
    """
    Тестирует все доступные камеры и позволяет переключаться между ними
    
    Управление:
    - 'q' - выход
    - 'n' - следующая камера
    - 'p' - предыдущая камера
    - '0'-'9' - прямое переключение на камеру с соответствующим индексом
    """
    available_cameras = list_available_cameras()
    
    if not available_cameras:
        print("Не найдено доступных камер.")
        return
    
    print(f"Найдено {len(available_cameras)} доступных камер: {available_cameras}")
    print("Управление:")
    print("  'q' - выход")
    print("  'n' - следующая камера")
    print("  'p' - предыдущая камера")
    print("  '0'-'9' - прямое переключение на камеру с соответствующим индексом")
    
    current_idx = 0
    current_camera = available_cameras[current_idx]
    
    # Создаем окно заранее
    cv2.namedWindow('Camera Test', cv2.WINDOW_NORMAL)
    
    cap = None
    
    def open_camera(camera_id):
        nonlocal cap
        # Закрываем предыдущую камеру, если она была открыта
        if cap is not None:
            cap.release()
        
        # Пробуем открыть камеру несколько раз
        for attempt in range(3):
            try:
                print(f"Попытка {attempt+1} открыть камеру {camera_id}")
                # Используем DirectShow для Windows
                new_cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
                
                if new_cap.isOpened():
                    # Проверяем, что можно получить кадр
                    ret, test_frame = new_cap.read()
                    if ret:
                        print(f"Камера {camera_id} успешно открыта")
                        return new_cap
                    else:
                        print(f"Не удалось получить кадр с камеры {camera_id}")
                        new_cap.release()
                else:
                    print(f"Не удалось открыть камеру {camera_id}")
                    if new_cap:
                        new_cap.release()
            except Exception as e:
                print(f"Ошибка при открытии камеры {camera_id}: {str(e)}")
                if 'new_cap' in locals() and new_cap:
                    new_cap.release()
            
            # Пауза перед следующей попыткой
            time.sleep(0.5)
        
        print(f"Не удалось открыть камеру {camera_id} после нескольких попыток")
        return None
    
    # Открываем первую камеру
    cap = open_camera(current_camera)
    
    while cap is not None:
        try:
            ret, frame = cap.read()
            
            if not ret:
                print(f"Не удалось получить кадр с камеры {current_camera}, пробуем переоткрыть")
                cap = open_camera(current_camera)
                if cap is None:
                    # Если не удалось переоткрыть текущую камеру, пробуем следующую
                    current_idx = (current_idx + 1) % len(available_cameras)
                    current_camera = available_cameras[current_idx]
                    cap = open_camera(current_camera)
                    if cap is None:
                        print("Не удалось открыть ни одну камеру")
                        break
                continue
            
            # Добавляем информацию о текущей камере на кадр
            cv2.putText(
                frame, 
                f"Camera: {current_camera} ({current_idx + 1}/{len(available_cameras)})", 
                (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1, 
                (0, 255, 0), 
                2
            )
            
            # Добавляем инструкции на кадр
            cv2.putText(
                frame, 
                "Press 'q' to exit, 'n' for next, 'p' for previous", 
                (10, frame.shape[0] - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, 
                (255, 255, 255), 
                2
            )
            
            # Показываем кадр
            cv2.imshow('Camera Test', frame)
            
            # Сохраняем кадр для отладки
            debug_dir = "debug_frames"
            os.makedirs(debug_dir, exist_ok=True)
            cv2.imwrite(f"{debug_dir}/camera_{current_camera}_frame.jpg", frame)
            
            # Обработка клавиш
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("Выход из программы")
                break
            elif key == ord('n'):
                # Переключение на следующую камеру
                current_idx = (current_idx + 1) % len(available_cameras)
                current_camera = available_cameras[current_idx]
                print(f"Переключение на камеру {current_camera}")
                cap = open_camera(current_camera)
            elif key == ord('p'):
                # Переключение на предыдущую камеру
                current_idx = (current_idx - 1) % len(available_cameras)
                current_camera = available_cameras[current_idx]
                print(f"Переключение на камеру {current_camera}")
                cap = open_camera(current_camera)
            # Добавляем прямое переключение на камеры по цифрам
            elif ord('0') <= key <= ord('9'):
                camera_num = key - ord('0')
                if camera_num < len(available_cameras):
                    current_idx = camera_num
                    current_camera = available_cameras[current_idx]
                    print(f"Прямое переключение на камеру {current_camera}")
                    cap = open_camera(current_camera)
                else:
                    print(f"Камера с индексом {camera_num} недоступна")
        except Exception as e:
            print(f"Ошибка в основном цикле: {str(e)}")
            # Пауза перед следующей итерацией
            time.sleep(0.5)
    
    # Закрываем ресурсы
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_cameras()