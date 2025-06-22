from fastapi import APIRouter, Request
from app.ml.yolo_detector import detect_people_from_image, model
from app.core.database import SessionLocal
from app.models.student import Attendance
import cv2
import numpy as np
import base64
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

router = APIRouter()

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

@router.post("/detect-image")
async def detect_image(request: Request):
    print("=== detect_image endpoint вызван ===", flush=True)
    print("Получен запрос detect-image", flush=True)
    print(await request.body(), flush=True)
    data = await request.json()
    image_data = data.get('image')
    model_name = data.get('model_name', 'yolov8n')
    if not image_data or ',' not in image_data:
        return {"count": 0, "model": model_name}
    image_data = image_data.split(',')[1]
    nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        return {"count": 0, "model": model_name}
    try:
        result = detect_people_from_image(img)
        return {"count": int(result["count"]), "boxes": result["boxes"], "model": model_name}
    except Exception as e:
        print("Ошибка в detect_people_from_image:", str(e), flush=True)
        return {"count": 0, "boxes": [], "model": model_name, "error": str(e)}