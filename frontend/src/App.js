import React, { useEffect, useRef, useState } from "react";

function App() {
  const [count, setCount] = useState(null);
  const [boxes, setBoxes] = useState([]);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  // 1) Запуск камеры
  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoRef.current.srcObject = stream;
      } catch (e) {
        console.error("Ошибка доступа к камере:", e);
      }
    };
    startCamera();
  }, []);

  // 2) Автодетект каждые 0.5 с
  useEffect(() => {
    const interval = setInterval(handleDetect, 500);
    return () => clearInterval(interval);
  }, []);

  // 3) Запрос к FastAPI
  const handleDetect = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/detect-live");
      const data = await res.json();
      setCount(data.count);
      setBoxes(data.boxes || []);
    } catch (e) {
      console.error("Ошибка при получении данных:", e);
    }
  };

  // 4) Отрисовка боксов на canvas
  useEffect(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || boxes.length === 0) return;

    // установим внутреннее разрешение канваса равным реальному потоку
    canvas.width  = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // теперь просто рисуем в тех же координатах, что и модель возвращает
    boxes.forEach(({ xmin, ymin, xmax, ymax }) => {
      ctx.strokeStyle = "red";
      ctx.lineWidth   = 2;
      ctx.strokeRect(xmin, ymin, xmax - xmin, ymax - ymin);
    });
  }, [boxes]);

  return (
    <div style={{ padding: "2rem", textAlign: "center", fontFamily: "Arial, sans-serif" }}>
      <h1>🎓 YOLO Student Counter</h1>

      <div style={{ position: "relative", display: "inline-block" }}>
        {/* видео */}
        <video
          ref={videoRef}
          autoPlay
          muted
          playsInline
          style={{ width: "640px", height: "auto" }}
        />
        {/* канвас с теми же CSS-размерами */}
        <canvas
          ref={canvasRef}
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: "640px",
            height: "auto",
            pointerEvents: "none",
          }}
        />
      </div>

      {count !== null && (
        <p style={{ marginTop: "1rem", fontSize: "18px" }}>🧍 Найдено: {count}</p>
      )}
    </div>
  );
}

export default App;