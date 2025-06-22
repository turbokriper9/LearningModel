import React, { useEffect, useRef, useState } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function App() {
  const [tab, setTab] = useState("main");
  const [count, setCount] = useState(null);
  const [boxes, setBoxes] = useState([]);
  const [stats, setStats] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [availableCameras, setAvailableCameras] = useState([]);
  const [selectedCamera, setSelectedCamera] = useState(0);
  const [videoDevices, setVideoDevices] = useState([]);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const detectTimeoutRef = useRef(null);
  const streamRef = useRef(null);

  // Получение списка доступных камер через MediaDevices API
  useEffect(() => {
    async function getVideoDevices() {
      try {
        // Запрашиваем разрешение на доступ к камере
        await navigator.mediaDevices.getUserMedia({ video: true });
        
        // Получаем список всех медиа-устройств
        const devices = await navigator.mediaDevices.enumerateDevices();
        
        // Фильтруем только видеоустройства (камеры)
        const videoDevs = devices.filter(device => device.kind === 'videoinput');
        console.log("Доступные видеоустройства:", videoDevs);
        
        setVideoDevices(videoDevs);
        setAvailableCameras(videoDevs.map((_, index) => index));
      } catch (err) {
        console.error("Ошибка при получении списка камер:", err);
        setError("Не удалось получить список камер");
      }
    }

    getVideoDevices();
  }, []);

  // Запуск камеры
  useEffect(() => {
    if (tab !== "main") return;
    
      const startCamera = async () => {
        try {
        // Останавливаем предыдущий стрим, если он существует
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
        }
        
        console.log(`Пытаемся открыть камеру с индексом ${selectedCamera}`);
        
        // Определяем deviceId выбранной камеры
        let constraints = { video: true };
        
        if (videoDevices.length > 0 && selectedCamera < videoDevices.length) {
          const deviceId = videoDevices[selectedCamera].deviceId;
          console.log(`Используем deviceId: ${deviceId}`);
          constraints = {
            video: { deviceId: { exact: deviceId } }
          };
        }
        
        // Запрашиваем доступ к выбранной камере
        const stream = await navigator.mediaDevices.getUserMedia(constraints);
        streamRef.current = stream;
        
          if (videoRef.current) {
            videoRef.current.srcObject = stream;
          }
        
        setError(null);
        } catch (e) {
        console.error(`Ошибка доступа к камере ${selectedCamera}:`, e);
        setError(`Не удалось получить доступ к камере ${selectedCamera}`);
        
        // Пробуем запасной вариант с камерой 0, если выбрана другая камера
        if (selectedCamera !== 0) {
          try {
            console.log("Пробуем запасной вариант с камерой 0");
            const fallbackStream = await navigator.mediaDevices.getUserMedia({ video: true });
            streamRef.current = fallbackStream;
            
            if (videoRef.current) {
              videoRef.current.srcObject = fallbackStream;
              setError("Используется запасная камера (0)");
            }
          } catch (fallbackError) {
            console.error("Ошибка доступа к запасной камере:", fallbackError);
            setError("Не удалось получить доступ ни к одной камере");
          }
        }
      }
    };
    
      startCamera();
    
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, [tab, selectedCamera, videoDevices]);

  // Обработчик переключения камеры
  const handleCameraChange = (cameraId) => {
    console.log(`Переключение на камеру ${cameraId}`);
    setSelectedCamera(cameraId);
    setError(null);
    setBoxes([]);
    setCount(null);
  };

  // Детекция людей каждую секунду
  useEffect(() => {
    if (tab !== "main") return;
    
    const detect = async () => {
      try {
      const video = videoRef.current;
      if (!video || !video.videoWidth || !video.videoHeight) return;
        
        setIsLoading(true);
        setError(null);
        
      const canvas = document.createElement("canvas");
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const dataUrl = canvas.toDataURL("image/jpeg");
        
        const res = await fetch("http://localhost:8000/api/v1/detect-image", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ image: dataUrl }),
        });
        
        if (!res.ok) {
          throw new Error(`Ошибка запроса: ${res.status}`);
        }
        
        const data = await res.json();
        setCount(data.count);
        setBoxes(data.boxes || []);
        if (data.error) {
          setError(data.error);
        }
      } catch (e) {
        console.error("Ошибка при распознавании:", e);
        setError("Ошибка распознавания");
        setCount(null);
        setBoxes([]);
      } finally {
        setIsLoading(false);
        
        // Запланировать следующее распознавание через 500 мс для более плавного отслеживания
        detectTimeoutRef.current = setTimeout(() => {
          if (tab === "main") {
            detect();
          }
        }, 500);
      }
    };

    // Запускаем первое распознавание
    const startDetection = () => {
      if (videoRef.current && videoRef.current.readyState >= 2) {
        detect();
      } else if (videoRef.current) {
        videoRef.current.onloadeddata = () => {
      detect();
        };
      }
    };
    
    startDetection();
    
    return () => {
      if (detectTimeoutRef.current) {
        clearTimeout(detectTimeoutRef.current);
      }
    };
  }, [tab, selectedCamera]);

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
    
    // Настройки для боксов
    ctx.lineWidth = 2;
    ctx.strokeStyle = "lime";
    ctx.fillStyle = "rgba(0, 255, 0, 0.2)";
    ctx.font = "16px Arial";
    ctx.textBaseline = "top";
    ctx.textAlign = "left";
    
    // Рисуем боксы с дополнительной информацией
    boxes.forEach((box, index) => {
      const width = box.xmax - box.xmin;
      const height = box.ymax - box.ymin;
      
      // Рисуем полупрозрачный фон
      ctx.fillRect(box.xmin, box.ymin, width, height);
      
      // Рисуем рамку
      ctx.strokeRect(box.xmin, box.ymin, width, height);
      
      // Добавляем номер объекта
      ctx.fillStyle = "white";
      ctx.strokeStyle = "black";
      ctx.lineWidth = 3;
      const text = `Объект ${index + 1}`;
      
      // Рисуем текст с обводкой
      ctx.strokeText(text, box.xmin, box.ymin - 20);
      ctx.fillText(text, box.xmin, box.ymin - 20);
      
      // Возвращаем стили для следующего бокса
      ctx.fillStyle = "rgba(0, 255, 0, 0.2)";
      ctx.strokeStyle = "lime";
      ctx.lineWidth = 2;
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
      const fetchStats = () => {
      fetch("http://localhost:8000/api/v1/attendance")
        .then((res) => res.json())
          .then((data) => {
            if (Array.isArray(data)) {
              console.log("Получены данные статистики:", data);
              setStats(data);
            } else {
              console.error("Неверный формат данных статистики:", data);
              setStats([]);
            }
          })
          .catch((error) => {
            console.error("Ошибка при получении статистики:", error);
            setStats([]);
          });
      };
      
      // Загружаем статистику сразу
      fetchStats();
      
      // И обновляем каждые 10 секунд
      const interval = setInterval(fetchStats, 10000);
      
      return () => clearInterval(interval);
    }
  }, [tab]);

  // Форматирование даты для отображения
  const formatDate = (isoString) => {
    try {
      const date = new Date(isoString);
      if (isNaN(date.getTime())) {
        console.error("Неверный формат даты:", isoString);
        return "Неверная дата";
      }
      
      // Форматируем время как ЧЧ:ММ, используя локальные настройки
      return date.toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false // 24-часовой формат
      });
    } catch (error) {
      console.error("Ошибка при форматировании даты:", error);
      return "Ошибка даты";
    }
  };

  // Готовим данные для линейного графика
  const chartData = {
    labels: stats.map((item) => formatDate(item.timestamp)).reverse(),
    datasets: [
      {
        label: "Количество студентов",
        data: stats.map((item) => item.count).reverse(),
        fill: false,
        borderColor: "rgb(75, 192, 192)",
        tension: 0.4,
        backgroundColor: "rgba(75, 192, 192, 0.5)",
        pointRadius: 5,
        pointHoverRadius: 7,
        pointBackgroundColor: "rgb(75, 192, 192)",
        pointBorderColor: "#fff",
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { 
        position: "top",
        labels: {
          boxWidth: 15,
          usePointStyle: true,
          pointStyle: "circle",
          font: {
            size: 14,
            weight: "bold"
          }
        }
      },
      title: { 
        display: true, 
        text: "Динамика количества студентов в аудитории",
        font: {
          size: 18,
          weight: "bold"
        },
        color: "#333",
        padding: {
          top: 10,
          bottom: 20
        }
      },
      tooltip: {
        mode: "index",
        intersect: false,
        backgroundColor: "rgba(0, 0, 0, 0.7)",
        titleFont: {
          size: 14,
          weight: "bold"
        },
        bodyFont: {
          size: 13
        },
        padding: 10,
        callbacks: {
          title: function(tooltipItems) {
            return `Время: ${tooltipItems[0].label}`;
          },
          label: function(context) {
            return `Студентов: ${context.parsed.y}`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1,
          precision: 0,
          font: {
            size: 12
          },
          color: "#666"
        },
        title: {
          display: true,
          text: "Количество студентов",
          font: {
            size: 14,
            weight: "bold"
          },
          color: "#666"
        },
        grid: {
          color: "rgba(0, 0, 0, 0.05)",
          drawBorder: false
        }
      },
      x: {
        ticks: {
          maxRotation: 45,
          minRotation: 45,
          font: {
            size: 12
          },
          color: "#666"
        },
        title: {
          display: true,
          text: "Время",
          font: {
            size: 14,
            weight: "bold"
          },
          color: "#666"
        },
        grid: {
          display: false,
          drawBorder: false
        }
      }
    },
    elements: {
      line: {
        borderWidth: 3,
        tension: 0.4 // Делает линию более плавной (кривой)
      }
    },
    interaction: {
      mode: "nearest",
      axis: "x",
      intersect: false
    },
    animation: {
      duration: 1000,
      easing: "easeOutQuart"
    }
  };

  // Компонент выбора камеры
  const CameraSelector = () => {
    return (
      <div className="camera-selector">
        <h3>Выбор камеры</h3>
        <div className="camera-buttons">
          {videoDevices.length > 0 ? (
            videoDevices.map((device, index) => (
              <button
                key={device.deviceId}
                onClick={() => handleCameraChange(index)}
                className={selectedCamera === index ? "active" : ""}
              >
                {device.label || `Камера ${index}`}
              </button>
            ))
          ) : (
            <p>Поиск доступных камер...</p>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="app">
      <header>
        <h1>
          <img src="/images/URFU.png" alt="УрФУ" className="logo" />
          Система подсчета студентов
        </h1>
        <div className="tabs">
          <button
            className={tab === "main" ? "active" : ""}
            onClick={() => setTab("main")}
          >
          Камера
        </button>
          <button
            className={tab === "stats" ? "active" : ""}
            onClick={() => setTab("stats")}
          >
            Статистика
          </button>
      </div>
      </header>

      <main>
        {tab === "main" ? (
          <div className="camera-tab">
            <div className="camera-container">
              <div className="video-wrapper">
          <video
            ref={videoRef}
            autoPlay
                  playsInline
            muted
                  className="camera-feed"
                />
                <canvas ref={canvasRef} className="detection-overlay" />
              </div>
              
              <CameraSelector />
              
              <div className="detection-info">
                {isLoading ? (
                  <div className="loading">Распознавание...</div>
                ) : error ? (
                  <div className="error">{error}</div>
                ) : count !== null ? (
                  <div className="count">
                    <span className="count-number">{count}</span>
                    <span className="count-label">
                      {count === 1
                        ? "студент"
                        : count >= 2 && count <= 4
                        ? "студента"
                        : "студентов"}
                    </span>
                  </div>
                ) : null}
              </div>
            </div>
          </div>
        ) : (
          <div className="stats-tab">
            <div className="chart-container">
              <h2>График посещаемости</h2>
              {stats.length > 0 ? (
                <Line
                  data={chartData}
                  options={{
                    responsive: true,
                    plugins: {
                      legend: {
                        position: "top",
                      },
                      tooltip: {
                        callbacks: {
                          label: function (context) {
                            return `Студентов: ${context.parsed.y}`;
                          },
                        },
                      },
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        ticks: {
                          stepSize: 1,
                        },
                        title: {
                          display: true,
                          text: "Количество студентов",
                        },
                      },
                      x: {
                        title: {
                          display: true,
                          text: "Время",
                        },
                      },
                    },
                  }}
                />
              ) : (
                <p className="no-data">Нет данных для отображения</p>
          )}
        </div>

            <div className="table-container">
              <h2>Таблица посещаемости</h2>
              {stats.length > 0 ? (
                <table className="stats-table">
                  <thead>
                    <tr>
                      <th>Время</th>
                      <th>Количество студентов</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats.map((item, index) => (
                      <tr key={index}>
                        <td>{formatDate(item.timestamp)}</td>
                        <td>{item.count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p className="no-data">Нет данных для отображения</p>
              )}
            </div>
        </div>
      )}
      </main>

      <style jsx>{`
        .app {
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          max-width: 1200px;
          margin: 0 auto;
          padding: 20px;
          color: #333;
        }
        
        header {
          display: flex;
          flex-direction: column;
          align-items: center;
          margin-bottom: 20px;
        }
        
        h1 {
          display: flex;
          align-items: center;
          font-size: 28px;
          margin-bottom: 20px;
        }
        
        .logo {
          height: 40px;
          margin-right: 15px;
        }
        
        .tabs {
          display: flex;
          gap: 10px;
          margin-bottom: 20px;
        }
        
        .tabs button {
          padding: 10px 20px;
          border: none;
          border-radius: 5px;
          background-color: #eee;
          cursor: pointer;
          font-size: 16px;
          transition: all 0.3s;
        }
        
        .tabs button.active {
          background-color: #4CAF50;
          color: white;
        }
        
        .camera-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          width: 100%;
        }
        
        .video-wrapper {
          position: relative;
          width: 100%;
          max-width: 800px;
          margin-bottom: 20px;
        }
        
        .camera-feed {
          width: 100%;
          border-radius: 8px;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        .detection-overlay {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          pointer-events: none;
        }
        
        .detection-info {
          margin-top: 20px;
          text-align: center;
        }
        
        .loading {
          font-size: 18px;
          color: #666;
        }
        
        .error {
          font-size: 18px;
          color: #f44336;
        }
        
        .count {
          display: flex;
          flex-direction: column;
          align-items: center;
        }
        
        .count-number {
          font-size: 48px;
          font-weight: bold;
          color: #4CAF50;
        }
        
        .count-label {
          font-size: 24px;
          color: #666;
        }
        
        .stats-tab {
          display: grid;
          grid-template-columns: 1fr;
          gap: 30px;
        }
        
        @media (min-width: 768px) {
          .stats-tab {
            grid-template-columns: 1fr 1fr;
          }
        }
        
        .chart-container, .table-container {
          background-color: white;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        h2 {
          margin-top: 0;
          margin-bottom: 20px;
          color: #333;
        }
        
        .stats-table {
          width: 100%;
          border-collapse: collapse;
        }
        
        .stats-table th, .stats-table td {
          padding: 10px;
          text-align: left;
          border-bottom: 1px solid #ddd;
        }
        
        .stats-table th {
          background-color: #f5f5f5;
          font-weight: bold;
        }
        
        .no-data {
          color: #666;
          font-style: italic;
        }
        
        .camera-selector {
          margin: 15px 0;
          text-align: center;
        }
        
        .camera-buttons {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
          justify-content: center;
        }
        
        .camera-buttons button {
          padding: 8px 15px;
          background-color: #f0f0f0;
          border: 1px solid #ddd;
          border-radius: 4px;
          cursor: pointer;
          transition: all 0.2s;
        }
        
        .camera-buttons button.active {
          background-color: #4CAF50;
          color: white;
          border-color: #4CAF50;
        }
        
        .camera-buttons button:hover:not(.active) {
          background-color: #e0e0e0;
        }
      `}</style>
    </div>
  );
}

export default App;