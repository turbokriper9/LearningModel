import cv2
from yolo_camera_project.app.ml.yolo_detector import detect_people_from_image

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Не удалось получить изображение с камеры.")
else:
    print("Камера работает! Нажмите 'q' чтобы выйти.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Не удалось считать кадр.")
            break

        # Детекция людей и рисование боксов
        result = detect_people_from_image(frame)
        for box in result["boxes"]:
            x1, y1, x2, y2 = box["xmin"], box["ymin"], box["xmax"], box["ymax"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        cv2.imshow('Live Camera, People Detection', frame)

        # Нажмите 'q', чтобы выйти
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()