import React, { useEffect, useRef, useState } from "react";

function App() {
  const [count, setCount] = useState(null);
  const [boxes, setBoxes] = useState([]);
  const videoRef = useRef(null);

  // Запускаем камеру при загрузке компонента
  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (error) {
        console.error("Ошибка доступа к камере:", error);
      }
    };

    startCamera();
  }, []);

  // Автоматическое обновление детекции каждые 5 секунд
  useEffect(() => {
    const interval = setInterval(() => {
      handleDetect();
    }, 1000); // 5000 мс = 5 секунд

    return () => clearInterval(interval); // Очистка при размонтировании
  }, []);

  const handleDetect = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/v1/detect-live");
      const data = await response.json();
      setCount(data.count);
      setBoxes(data.boxes || []);
    } catch (error) {
      console.error("Ошибка при получении данных:", error);
    }
  };

  return (
    <div
      style={{
        padding: "2rem",
        fontFamily: "Arial, sans-serif",
        maxWidth: "800px",
        margin: "auto",
      }}
    >
      <h1>
        🎓 <b>YOLO Student Counter</b>
      </h1>

      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        style={{ width: "100%", borderRadius: "10px", marginBottom: "1rem" }}
      />

      <button
        onClick={handleDetect}
        style={{
          padding: "10px 20px",
          backgroundColor: "#2563eb",
          color: "white",
          border: "none",
          borderRadius: "5px",
          cursor: "pointer",
        }}
      >
        🎥 Обновить вручную
      </button>

      {count !== null && (
        <div style={{ marginTop: "1rem", fontSize: "18px" }}>
          🧍 Найдено студентов: <b>{count}</b>
        </div>
      )}

      {boxes.length > 0 && (
        <div
          style={{
            backgroundColor: "#f3f4f6",
            padding: "1rem",
            marginTop: "1rem",
            borderRadius: "8px",
          }}
        >
          <b>📦 Координаты:</b>
          <ul>
            {boxes.map((box, index) => (
              <li key={index}>
                #{index + 1}: (xmin: {Math.round(box.xmin)}, ymin:{" "}
                {Math.round(box.ymin)}, xmax: {Math.round(box.xmax)}, ymax:{" "}
                {Math.round(box.ymax)})
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;