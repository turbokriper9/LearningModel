from fastapi import APIRouter
from app.ml.yolo_detector import detect_people_from_camera

router = APIRouter()

@router.get("/detect-live")
async def detect_live():
    """
     Запуск детекции студентов в реальном времени с камеры.
    """
    result = detect_people_from_camera()
    return result