from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.student import Attendance
from pydantic import BaseModel
import datetime
from typing import Optional, Dict, Any
from sqlalchemy import func

router = APIRouter()

class AttendanceCreate(BaseModel):
    count: int
    lesson_number: Optional[int] = None

class AttendanceRead(BaseModel):
    id: int
    timestamp: datetime.datetime
    count: int
    lesson_number: Optional[int] = None
    date: Optional[datetime.date] = None

    class Config:
        orm_mode = True

class LessonStatistics(BaseModel):
    max_count: int
    current_count: Optional[int] = None
    time_series: list[Dict[str, Any]]

# Вспомогательная функция для определения номера пары по времени
def get_lesson_number(time):
    hour, minute = time.hour, time.minute
    
    # Расписание пар
    lesson_schedule = [
        (8, 30, 10, 0),     # 1 пара: 8:30-10:00
        (10, 15, 11, 45),   # 2 пара: 10:15-11:45
        (12, 0, 13, 30),    # 3 пара: 12:00-13:30
        (14, 15, 15, 45),   # 4 пара: 14:15-15:45
        (16, 0, 17, 30),    # 5 пара: 16:00-17:30
        (17, 40, 19, 10),   # 6 пара: 17:40-19:10
        (19, 15, 20, 45),   # 7 пара: 19:15-20:45
        (20, 50, 22, 20)    # 8 пара: 20:50-22:20
    ]
    
    current_time_minutes = hour * 60 + minute
    
    for idx, (start_h, start_m, end_h, end_m) in enumerate(lesson_schedule):
        start_minutes = start_h * 60 + start_m
        end_minutes = end_h * 60 + end_m
        
        if start_minutes <= current_time_minutes <= end_minutes:
            return idx + 1  # Номера пар начинаются с 1
            
    return None  # Вне расписания пар

@router.post("/attendance", response_model=AttendanceRead)
def create_attendance(att: AttendanceCreate, db: Session = Depends(get_db)):
    """
    Создать новую запись о посещаемости
    """
    # Если номер пары не указан, определяем его автоматически
    lesson_number = att.lesson_number
    if lesson_number is None:
        current_time = datetime.datetime.now()
        lesson_number = get_lesson_number(current_time)
    
    row = Attendance(
        count=att.count, 
        lesson_number=lesson_number,
        date=datetime.datetime.now().date()
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

@router.get("/attendance", response_model=list[AttendanceRead])
def read_attendance(
    skip: int = 0, 
    limit: int = 100, 
    lesson_number: Optional[int] = None,
    date: Optional[datetime.date] = None,
    db: Session = Depends(get_db)
):
    """
    Получить историю посещаемости с возможностью фильтрации по номеру пары и дате
    """
    query = db.query(Attendance)
    
    # Применяем фильтры, если они указаны
    if lesson_number is not None:
        query = query.filter(Attendance.lesson_number == lesson_number)
    
    if date is not None:
        query = query.filter(Attendance.date == date)
    
    return query.order_by(Attendance.timestamp.desc()).offset(skip).limit(limit).all()

@router.get("/attendance/by-lesson", response_model=list[AttendanceRead])
def get_attendance_by_lesson(
    date: Optional[datetime.date] = None,
    db: Session = Depends(get_db)
):
    """
    Получить последние записи посещаемости для каждой пары на указанную дату
    """
    # Устанавливаем текущую дату, если не указана
    if date is None:
        date = datetime.datetime.now().date()
    
    # Создаем подзапрос для получения последней записи по каждой паре
    subquery = db.query(
        Attendance.lesson_number,
        func.max(Attendance.timestamp).label('max_timestamp')
    ).filter(Attendance.date == date).group_by(Attendance.lesson_number).subquery()
    
    # Соединяем с основной таблицей, чтобы получить полные записи
    query = db.query(Attendance).join(
        subquery,
        (Attendance.lesson_number == subquery.c.lesson_number) & 
        (Attendance.timestamp == subquery.c.max_timestamp)
    )
    
    return query.order_by(Attendance.lesson_number).all()

@router.get("/attendance/daily-stats")
def get_daily_stats(
    date: Optional[datetime.date] = None,
    db: Session = Depends(get_db)
):
    """
    Получить статистику посещаемости по парам за указанный день
    """
    if date is None:
        date = datetime.datetime.now().date()
    
    # Получаем максимальное количество студентов для каждой пары
    result = {}
    for lesson_num in range(1, 9):  # Для пар с 1 по 8
        max_count = db.query(func.max(Attendance.count)).filter(
            Attendance.date == date,
            Attendance.lesson_number == lesson_num
        ).scalar()
        
        result[f"lesson_{lesson_num}"] = max_count or 0
    
    # Добавляем информацию о расписании пар
    lesson_schedule = {
        "lesson_1": "8:30-10:00",
        "lesson_2": "10:15-11:45",
        "lesson_3": "12:00-13:30",
        "lesson_4": "14:15-15:45",
        "lesson_5": "16:00-17:30",
        "lesson_6": "17:40-19:10",
        "lesson_7": "19:15-20:45",
        "lesson_8": "20:50-22:20"
    }
    
    return {
        "date": date.isoformat(),
        "attendance": result,
        "schedule": lesson_schedule
    }

@router.get("/attendance/lesson-stats")
def get_lesson_stats(
    lesson_number: int,
    date: Optional[datetime.date] = None,
    db: Session = Depends(get_db)
):
    """
    Получить детальную статистику по конкретной паре:
    - максимальное количество студентов
    - временной ряд посещаемости
    """
    if date is None:
        date = datetime.datetime.now().date()
    
    # Получаем максимальное количество студентов для указанной пары
    max_count = db.query(func.max(Attendance.count)).filter(
        Attendance.date == date,
        Attendance.lesson_number == lesson_number
    ).scalar() or 0
    
    # Получаем временной ряд посещаемости для данной пары
    time_series_query = db.query(Attendance).filter(
        Attendance.date == date,
        Attendance.lesson_number == lesson_number
    ).order_by(Attendance.timestamp.asc())
    
    time_series = []
    for record in time_series_query:
        time_series.append({
            "timestamp": record.timestamp.isoformat(),
            "count": record.count
        })
    
    # Получаем текущее/последнее количество студентов
    current_count = time_series[-1]["count"] if time_series else None
    
    # Время начала и окончания пары
    lesson_times = {
        1: "8:30-10:00",
        2: "10:15-11:45",
        3: "12:00-13:30",
        4: "14:15-15:45",
        5: "16:00-17:30",
        6: "17:40-19:10",
        7: "19:15-20:45",
        8: "20:50-22:20"
    }
    
    return {
        "date": date.isoformat(),
        "lesson_number": lesson_number,
        "lesson_time": lesson_times.get(lesson_number, "Неизвестное время"),
        "max_count": max_count,
        "current_count": current_count,
        "time_series": time_series
    }