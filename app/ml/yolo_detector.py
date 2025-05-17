import cv2
import torch

model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

def detect_people_from_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return 0, [{"error": "Камера не открылась"}]

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return 0, [{"error": "Не удалось получить кадр с камеры"}]

    results = model(frame)
    df = results.pandas().xyxy[0]
    people = df[df['name'] == 'person']
    boxes = people[['xmin', 'ymin', 'xmax', 'ymax']].to_dict(orient="records")
    return len(people), boxes