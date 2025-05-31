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
  const [stats, setStats] = useState([]);
  const videoRef = useRef(null);

  // Камера и детекция (можно упростить если не нужна автодетекция)
  useEffect(() => {
    if (tab === "main") {
      const startCamera = async () => {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ video: true });
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
          }
        } catch (e) {
          console.error("Ошибка доступа к камере:", e);
        }
      };
      startCamera();

      // Опционально: автоматическая детекция (если нужен счетчик)
      const interval = setInterval(handleDetect, 2000); // каждые 2 сек
      return () => clearInterval(interval);
    }
  }, [tab]);

  // Получение статистики при переключении во вкладку "Статистика"
  useEffect(() => {
    if (tab === "stats") {
      fetch("http://localhost:8000/api/v1/attendance")
        .then((res) => res.json())
        .then((data) => setStats(Array.isArray(data) ? data : []))
        .catch(() => setStats([]));
    }
  }, [tab]);

  const handleDetect = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/detect-live");
      const data = await res.json();
      setCount(data.count);
    } catch (e) {
      setCount(null);
    }
  };

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
        <div>
          <video ref={videoRef} autoPlay muted playsInline style={{ width: "640px" }} />
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