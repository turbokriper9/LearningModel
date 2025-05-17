from fastapi import APIRouter
from app.ml.yolo_detector import detect_people_from_camera

router = APIRouter()

@router.get("/detect-live")
def detect_live():
    count, result = detect_people_from_camera()
    return {"count": count, "boxes": result}