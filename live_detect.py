#!/usr/bin/env python3
import cv2
from ultralytics import YOLO

def main():
    # 1) Укажи путь к своему файлу best.pt
    model = YOLO("runs/detect/train2/weights/best.pt")

    # 2) Открываем камеру (0 — встроенная, 1, 2… — внешние)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Не удалось открыть камеру")
        return

    print("✅ Камера открыта. Нажми 'q' для выхода.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Не удалось считать кадр")
            break

        # 3) Запускаем детекцию на каждом кадре
        #    imgsz — размер кадра, conf — порог уверенности
        results = model(frame, imgsz=640, conf=0.5)

        # 4) Рисуем боксами/метками прямо на кадре
        annotated_frame = results[0].plot()

        # (опционально) можно также вывести просто количество:
        # count = sum(1 for b in results[0].boxes if model.names[int(b.cls[0])] == "person")
        # cv2.putText(annotated_frame, f"Count: {count}", (10,30),
        #             cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        # 5) Показываем результат
        cv2.imshow("Live Detection", annotated_frame)

        # 6) Выход по q
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()