from ultralytics import YOLO
import cv2
import base64

# Используем только headmodel для людей
model = YOLO("runs/detect/lasttrain/weights/headmodel.pt")

def detect_people_from_image(img):
    results = model(img)
    detections = results[0].boxes
    count = 0
    boxes = []
    for box in detections:
        if int(box.cls[0]) == 0:  # 0 — класс person
            count += 1
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            boxes.append({"xmin": x1, "ymin": y1, "xmax": x2, "ymax": y2})
    return {"count": count, "boxes": boxes}

def detect_people_from_camera():
    cap = cv2.VideoCapture(0)
    success, frame = cap.read()
    cap.release()

    if not success:
        return {"count": 0, "boxes": []}

    results = model(frame)
    detections = results[0].boxes
    count = 0
    boxes = []
    for box in detections:
        if int(box.cls[0]) == 0:  # 0 — класс person
            count += 1
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            boxes.append({"xmin": x1, "ymin": y1, "xmax": x2, "ymax": y2})
    return {"count": count, "boxes": boxes}