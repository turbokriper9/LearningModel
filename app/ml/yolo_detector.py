from ultralytics import YOLO
import cv2

model = YOLO("runs/detect/train/weights/finalyolov11.pt")

def detect_people_from_camera():
    cap = cv2.VideoCapture(0)
    success, frame = cap.read()
    cap.release()

    if not success:
        return {"count": 0, "boxes": []}

    results = model(frame)
    detections = results[0].boxes.data.cpu().numpy()

    count = len(detections)
    boxes = []
    for det in detections:
        x1, y1, x2, y2 = map(int, det[:4])
        boxes.append({"xmin": x1, "ymin": y1, "xmax": x2, "ymax": y2})

    return {"count": count, "boxes": boxes}

def detect_people_from_image(img):
    print("Классы модели:", model.names, flush=True)
    cv2.imwrite("debug.jpg", img)  # Сохраняем изображение для отладки
    results = model(img)
    detections = results[0].boxes
    count = 0
    boxes = []
    for box in detections:
        if int(box.cls[0]) == 0:  # 0 — класс person
            count += 1
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            boxes.append({"xmin": x1, "ymin": y1, "xmax": x2, "ymax": y2})
    print("Обнаружено людей:", count)
    return {"count": count, "boxes": boxes}

print("Shape:", img.shape if img is not None else "None")