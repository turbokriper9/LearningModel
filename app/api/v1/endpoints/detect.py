from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.ml.yolo_detector import detect_people_from_camera, detect_people_from_image
from app.core.database import get_db
from app.models.student import Attendance
from pydantic import BaseModel
from typing import List, Dict, Any
import base64
import cv2
import numpy as np
import time
import datetime

router = APIRouter()

# Переменные для отслеживания изменений в количестве людей
last_count = None
last_db_save_time = 0
MIN_SAVE_INTERVAL = 5  # минимальный интервал между записями в БД (в секундах)

class DetectionResult(BaseModel):
    count: int
    boxes: List[Dict[str, Any]]

class ImageRequest(BaseModel):
    image: str  # base64 encoded image

class AttendanceRecord(BaseModel):
    timestamp: str
    count: int

@router.get("/detect-live", response_model=DetectionResult)
async def detect_live(db: Session = Depends(get_db)):
    """
    Запуск детекции студентов в реальном времени с камеры и запись в БД.
    """
    result = detect_people_from_camera()

    # Сохраняем историю в БД
    attendance = Attendance(count=result['count'])
    db.add(attendance)
    db.commit()
    db.refresh(attendance)

    return result

@router.post("/detect-image", response_model=DetectionResult)
async def detect_image(request: ImageRequest, db: Session = Depends(get_db)):
    """
    Детекция студентов из загруженного изображения и запись в БД.
    """
    global last_count, last_db_save_time
    
    try:
        # Декодируем base64 изображение
        image_data = request.image.split(',')[1] if ',' in request.image else request.image
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return {"count": 0, "boxes": []}
        
        # Запускаем детекцию
        result = detect_people_from_image(img)
        current_count = result['count']
        current_time = time.time()
        
        # Корректируем количество для статистики (вычитаем 1)
        adjusted_count = max(0, current_count - 1)
        
        # Записываем в БД каждые 3 секунды, если скорректированное количество людей > 0
        if adjusted_count > 0 and (current_time - last_db_save_time >= 3):
            print(f"Сохраняем в БД: исходное количество = {current_count}, скорректированное = {adjusted_count}, время = {datetime.datetime.now()}")
            attendance = Attendance(count=adjusted_count)
            db.add(attendance)
            db.commit()
            
            # Обновляем время последней записи
            last_db_save_time = current_time
        
        # Обновляем последнее количество
        last_count = current_count
        
        return result
    except Exception as e:
        print(f"Ошибка при обработке изображения: {str(e)}")
        return {"count": 0, "boxes": []}

@router.get("/attendance", response_model=List[AttendanceRecord])
async def attendance(db: Session = Depends(get_db)):
    """
    Получить историю посещаемости для фронтенда.
    """
    # Получаем только записи с count > 0
    records = db.query(Attendance).filter(Attendance.count > 0).order_by(Attendance.timestamp.desc()).limit(50).all()
    
    print(f"Найдено {len(records)} записей с ненулевым количеством людей")
    
    # Преобразуем время в локальный часовой пояс и форматируем
    result = []
    for rec in records:
        # Преобразуем UTC время в локальное
        local_time = rec.timestamp.replace(tzinfo=datetime.timezone.utc).astimezone()
        result.append({
            "timestamp": local_time.isoformat(),
            "count": rec.count
        })
    
    return result

@router.get("/attendance-history")
async def attendance_history(db: Session = Depends(get_db)):
    """
    Получить историю посещаемости.
    """
    records = db.query(Attendance).order_by(Attendance.timestamp.asc()).all()
    return [
        {"timestamp": rec.timestamp.isoformat(), "count": rec.count}
        for rec in records
    ]