from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.ml.yolo_detector import detect_people_from_camera, detect_people_from_image, get_available_cameras
from app.core.database import get_db
from app.models.student import Attendance
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import base64
import cv2
import numpy as np
import time
import datetime
import traceback
from collections import defaultdict

router = APIRouter()

# Переменные для отслеживания изменений в количестве людей
last_count = None
last_db_save_time = 0
MIN_SAVE_INTERVAL = 10  # минимальный интервал между записями в БД (в секундах)

class DetectionResult(BaseModel):
    count: int
    boxes: List[Dict[str, Any]]
    camera_id: Optional[int] = 0
    error: Optional[str] = None

class CameraInfo(BaseModel):
    id: int
    name: str
    available: bool

class ImageRequest(BaseModel):
    image: str  # base64 encoded image

class AttendanceRecord(BaseModel):
    timestamp: str
    count: int

class DayStatistics(BaseModel):
    day: str
    average_count: float
    max_count: int
    total_records: int

class HourStatistics(BaseModel):
    hour: int
    average_count: float
    max_count: int
    total_records: int

@router.get("/detect-live", response_model=DetectionResult)
async def detect_live(camera_id: int = Query(0, description="ID камеры (0 - встроенная, 1+ - внешние)"), db: Session = Depends(get_db)):
    """
    Запуск детекции студентов в реальном времени с камеры и запись в БД.
    
    - **camera_id**: ID камеры (0 - встроенная, 1+ - внешние)
    """
    try:
        print(f"Запрос на детекцию с камеры {camera_id}")
        result = detect_people_from_camera(camera_id)
        
        # Проверяем наличие ошибок
        if "error" in result and result["error"]:
            print(f"Ошибка при детекции с камеры {camera_id}: {result['error']}")
        else:
            # Сохраняем историю в БД только если нет ошибок
            try:
                attendance = Attendance(count=result['count'])
                db.add(attendance)
                db.commit()
                db.refresh(attendance)
                print(f"Сохранено в БД: камера {camera_id}, количество людей: {result['count']}")
            except Exception as e:
                print(f"Ошибка при сохранении в БД: {str(e)}")
                traceback.print_exc()

        return result
    except Exception as e:
        print(f"Необработанная ошибка в detect-live: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {str(e)}")

@router.get("/available-cameras", response_model=Dict[str, List[CameraInfo]])
async def available_cameras():
    """
    Получить список доступных камер в системе
    """
    try:
        cameras = get_available_cameras()
        camera_info = [
            CameraInfo(
                id=camera_id,
                name=f"Камера {camera_id}",
                available=True
            ) for camera_id in cameras
        ]
        
        # Если камеры не найдены, добавляем хотя бы одну
        if not camera_info:
            camera_info.append(CameraInfo(id=0, name="Основная камера", available=True))
            
        return {"available_cameras": camera_info}
    except Exception as e:
        print(f"Ошибка при получении списка камер: {str(e)}")
        traceback.print_exc()
        # Возвращаем хотя бы одну камеру в случае ошибки
        return {"available_cameras": [CameraInfo(id=0, name="Основная камера", available=True)]}

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
            return {"count": 0, "boxes": [], "error": "Не удалось декодировать изображение"}
        
        # Запускаем детекцию
        result = detect_people_from_image(img)
        current_count = result['count']
        current_time = time.time()
        
        # Корректируем количество для статистики (вычитаем 1)
        adjusted_count = max(0, current_count - 1)
        
        # Записываем в БД каждые 10 секунд, если скорректированное количество людей > 0
        if adjusted_count > 0 and (current_time - last_db_save_time >= MIN_SAVE_INTERVAL):
            now = datetime.datetime.now()
            print(f"Сохраняем в БД: исходное количество = {current_count}, скорректированное = {adjusted_count}, время = {now}")
            try:
                attendance = Attendance(count=adjusted_count, timestamp=now)
                db.add(attendance)
                db.commit()
                
                # Обновляем время последней записи
                last_db_save_time = current_time
            except Exception as e:
                print(f"Ошибка при сохранении в БД: {str(e)}")
                traceback.print_exc()
        
        # Обновляем последнее количество
        last_count = current_count
        
        return result
    except Exception as e:
        print(f"Ошибка при обработке изображения: {str(e)}")
        traceback.print_exc()
        return {"count": 0, "boxes": [], "error": str(e)}

@router.get("/attendance", response_model=List[AttendanceRecord])
async def attendance(db: Session = Depends(get_db)):
    """
    Получить историю посещаемости для фронтенда.
    """
    try:
        # Получаем только записи с count > 0
        records = db.query(Attendance).filter(Attendance.count > 0).order_by(Attendance.timestamp.desc()).limit(50).all()
        
        print(f"Найдено {len(records)} записей с ненулевым количеством людей")
        
        # Используем локальное время без преобразования из UTC
        result = []
        for rec in records:
            result.append({
                "timestamp": rec.timestamp.isoformat(),
                "count": rec.count
            })
        
        return result
    except Exception as e:
        print(f"Ошибка при получении истории посещаемости: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка при получении данных из БД: {str(e)}")

@router.get("/attendance-history")
async def attendance_history(db: Session = Depends(get_db)):
    """
    Получить историю посещаемости.
    """
    try:
        records = db.query(Attendance).order_by(Attendance.timestamp.asc()).all()
        return [
            {"timestamp": rec.timestamp.isoformat(), "count": rec.count}
            for rec in records
        ]
    except Exception as e:
        print(f"Ошибка при получении истории посещаемости: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка при получении данных из БД: {str(e)}")

@router.get("/attendance-by-day", response_model=List[DayStatistics])
async def attendance_by_day(db: Session = Depends(get_db)):
    """
    Получить статистику посещаемости по дням недели.
    """
    try:
        # Получаем все записи
        records = db.query(Attendance).all()
        
        # Группируем по дням недели
        days_data = defaultdict(list)
        days_order = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        days_map = {
            0: "Понедельник",
            1: "Вторник",
            2: "Среда",
            3: "Четверг",
            4: "Пятница",
            5: "Суббота",
            6: "Воскресенье"
        }
        
        for record in records:
            # Получаем день недели (0-6, где 0 - понедельник)
            day_of_week = record.timestamp.weekday()
            day_name = days_map[day_of_week]
            days_data[day_name].append(record.count)
        
        # Формируем результат
        result = []
        for day in days_order:
            counts = days_data.get(day, [])
            if counts:
                result.append({
                    "day": day,
                    "average_count": round(sum(counts) / len(counts), 2),
                    "max_count": max(counts),
                    "total_records": len(counts)
                })
            else:
                result.append({
                    "day": day,
                    "average_count": 0,
                    "max_count": 0,
                    "total_records": 0
                })
        
        return result
    except Exception as e:
        print(f"Ошибка при получении статистики по дням: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка при получении данных из БД: {str(e)}")

@router.get("/attendance-by-hour", response_model=List[HourStatistics])
async def attendance_by_hour(db: Session = Depends(get_db)):
    """
    Получить статистику посещаемости по часам суток.
    """
    try:
        # Получаем все записи
        records = db.query(Attendance).all()
        
        # Группируем по часам
        hours_data = defaultdict(list)
        
        for record in records:
            # Получаем час (0-23)
            hour = record.timestamp.hour
            hours_data[hour].append(record.count)
        
        # Формируем результат
        result = []
        for hour in range(24):  # 24 часа
            counts = hours_data.get(hour, [])
            if counts:
                result.append({
                    "hour": hour,
                    "average_count": round(sum(counts) / len(counts), 2),
                    "max_count": max(counts),
                    "total_records": len(counts)
                })
            else:
                result.append({
                    "hour": hour,
                    "average_count": 0,
                    "max_count": 0,
                    "total_records": 0
                })
        
        return result
    except Exception as e:
        print(f"Ошибка при получении статистики по часам: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Ошибка при получении данных из БД: {str(e)}")