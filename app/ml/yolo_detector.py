from ultralytics import YOLO
import cv2

#модель YOLOv8
model = YOLO("runs/detect/train3/weights/best.pt")

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