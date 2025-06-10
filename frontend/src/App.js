import React, { useEffect, useRef, useState } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function App() {
  const [tab, setTab] = useState("main");
  const [count, setCount] = useState(null);
  const [boxes, setBoxes] = useState([]);
  const [stats, setStats] = useState([]);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  // Запуск камеры
  useEffect(() => {
    if (tab !== "main") return;
    let stream;
    const startCamera = async () => {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (e) {
        console.error("Ошибка доступа к камере:", e);
      }
    };
    startCamera();
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [tab]);

  // Детекция людей раз в 2 секунды
  useEffect(() => {
    if (tab !== "main") return;
    let interval;
    const detect = async () => {
      const video = videoRef.current;
      if (!video || !video.videoWidth || !video.videoHeight) return;
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const dataUrl = canvas.toDataURL("image/jpeg");
      try {
        const res = await fetch("http://localhost:8000/api/v1/detect-image", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ image: dataUrl }),
        });
        const data = await res.json();
        setCount(data.count);
        setBoxes(data.boxes || []);
      } catch (e) {
        setCount(null);
        setBoxes([]);
      }
    };
    // Первый запуск после загрузки видео
    const onLoaded = () => {
      detect();
      interval = setInterval(detect, 2000);
    };
    if (videoRef.current) {
      videoRef.current.onloadedmetadata = onLoaded;
    }
    return () => {
      if (interval) clearInterval(interval);
      if (videoRef.current) videoRef.current.onloadedmetadata = null;
    };
    // eslint-disable-next-line
  }, [tab]);

  // Рисование боксов и отладка
  useEffect(() => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;
    if (!video.videoWidth || !video.videoHeight) return;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.lineWidth = 2;
    ctx.strokeStyle = "lime";
    boxes.forEach((box) => {
      ctx.strokeRect(
        box.xmin,
        box.ymin,
        box.xmax - box.xmin,
        box.ymax - box.ymin
      );
    });
    // Отладка
    console.log("video size:", video.videoWidth, video.videoHeight);
    console.log("canvas size:", canvas.width, canvas.height);
    console.log("boxes:", boxes);
  }, [boxes, tab]);

  // Дополнительная отладка: выводим обновление боксов
  useEffect(() => {
    console.log("boxes state updated:", boxes);
  }, [boxes]);

  // Получение статистики при переключении во вкладку "Статистика"
  useEffect(() => {
    if (tab === "stats") {
      fetch("http://localhost:8000/api/v1/attendance")
        .then((res) => res.json())
        .then((data) => setStats(Array.isArray(data) ? data : []))
        .catch(() => setStats([]));
    }
  }, [tab]);

  // Готовим данные для графика
  const chartData = {
    labels: stats.map((item) => {
      const date = new Date(item.timestamp);
      return `${date.getHours()}:${date.getMinutes().toString().padStart(2, "0")}`;
    }),
    datasets: [
      {
        label: "Посещаемость",
        data: stats.map((item) => item.count),
        backgroundColor: "#2563eb",
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: { position: "top" },
      title: { display: true, text: "Статистика посещаемости по времени" },
    },
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial, sans-serif", textAlign: "center" }}>
      <h1>🎓 YOLO Student Counter</h1>
      <div style={{ marginBottom: "1rem" }}>
        <button onClick={() => setTab("main")} style={{ marginRight: "1rem" }}>
          Камера
        </button>
        <button onClick={() => setTab("stats")}>Статистика</button>
      </div>
      {tab === "main" && (
        <div style={{ position: "relative", display: "inline-block" }}>
          <video
            ref={videoRef}
            autoPlay
            muted
            playsInline
            style={{ width: "640px", height: "480px" }}
            width={640}
            height={480}
          />
          <canvas
            ref={canvasRef}
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              pointerEvents: "none",
              width: "640px",
              height: "480px",
            }}
            width={640}
            height={480}
          />
          {count !== null && (
            <p style={{ marginTop: "1rem", fontSize: "18px" }}>🧍 Найдено: {count}</p>
          )}
        </div>
      )}
      {tab === "stats" && (
        <div>
          <h2>Посещаемость по времени</h2>
          {Array.isArray(stats) && stats.length > 0 ? (
            <Bar data={chartData} options={chartOptions} />
          ) : (
            <p>Нет данных для отображения</p>
          )}
        </div>
      )}
    </div>
  );
}

export default App;