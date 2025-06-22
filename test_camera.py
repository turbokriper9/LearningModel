import cv2

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

        cv2.imshow('Live Camera, DANGER!', frame)

        # Нажмите 'q', чтобы выйти
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()