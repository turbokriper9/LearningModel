from fastapi import APIRouter
from app.ml.yolo_detector import detect_people_from_camera
from app.core.database import SessionLocal
from app.models.student import Attendance

router = APIRouter()

@router.get("/detect-live")
async def detect_live():
    """
    Запуск детекции студентов в реальном времени с камеры и запись в БД.
    """
    result = detect_people_from_camera()

    # Сохраняем историю в БД
    db = SessionLocal()
    attendance = Attendance(count=result['count'])
    db.add(attendance)
    db.commit()
    db.close()

    return result

@router.get("/attendance-history")
async def attendance_history():
    """
    Получить историю посещаемости.
    """
    db = SessionLocal()
    records = db.query(Attendance).order_by(Attendance.timestamp.asc()).all()
    db.close()
    return [
        {"timestamp": rec.timestamp.isoformat(), "count": rec.count}
        for rec in records
    ]