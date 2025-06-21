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
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const detectTimeoutRef = useRef(null);

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
      
      // Форматируем время как ЧЧ:ММ
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
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
        pointBorderWidth: 2,
      }
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

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial, sans-serif", textAlign: "center", backgroundColor: "#f8f9fa" }}>
      <h1 style={{ color: "#333", marginBottom: "1.5rem" }}>🎓 YOLO Student Counter</h1>
      <div style={{ marginBottom: "1.5rem" }}>
        <button 
          onClick={() => setTab("main")} 
          style={{ 
            marginRight: "1rem", 
            padding: "10px 20px", 
            backgroundColor: tab === "main" ? "#4c6ef5" : "#e9ecef",
            color: tab === "main" ? "white" : "#333",
            border: "none",
            borderRadius: "5px",
            cursor: "pointer",
            fontWeight: "bold",
            transition: "all 0.3s"
          }}
        >
          Камера
        </button>
        <button 
          onClick={() => setTab("stats")} 
          style={{ 
            padding: "10px 20px", 
            backgroundColor: tab === "stats" ? "#4c6ef5" : "#e9ecef",
            color: tab === "stats" ? "white" : "#333",
            border: "none",
            borderRadius: "5px",
            cursor: "pointer",
            fontWeight: "bold",
            transition: "all 0.3s"
          }}
        >
          Статистика
        </button>
      </div>
      {tab === "main" && (
        <div style={{ position: "relative", display: "inline-block" }}>
          <video
            ref={videoRef}
            autoPlay
            muted
            playsInline
            style={{ 
              width: "640px", 
              height: "480px", 
              borderRadius: "8px", 
              boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)" 
            }}
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
              borderRadius: "8px"
            }}
            width={640}
            height={480}
          />
          {isLoading && (
            <div style={{ 
              position: "absolute", 
              top: "10px", 
              right: "10px", 
              background: "rgba(0,0,0,0.5)", 
              color: "white",
              padding: "5px 10px",
              borderRadius: "5px"
            }}>
              Распознавание...
            </div>
          )}
          {error && (
            <div style={{ 
              position: "absolute", 
              top: "10px", 
              right: "10px", 
              background: "rgba(255,0,0,0.7)", 
              color: "white",
              padding: "5px 10px",
              borderRadius: "5px"
            }}>
              {error}
            </div>
          )}
          <div style={{ 
            marginTop: "1rem", 
            padding: "1rem", 
            backgroundColor: "white", 
            borderRadius: "8px",
            boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
          }}>
            <h3 style={{ margin: "0 0 0.5rem 0", color: "#333" }}>Информация о распознавании</h3>
            <div style={{ display: "flex", justifyContent: "center", gap: "2rem" }}>
              <div>
                <p style={{ fontWeight: "bold", fontSize: "24px", margin: "0", color: "#4c6ef5" }}>
                  🧍 Найдено: {count !== null ? count : "—"}
                </p>
                <p style={{ margin: "0.5rem 0 0 0", color: "#666" }}>
                  Обнаруженных объектов
                </p>
              </div>
              <div>
                <p style={{ fontWeight: "bold", fontSize: "24px", margin: "0", color: "#4c6ef5" }}>
                  ⏱️ {new Date().toLocaleTimeString()}
                </p>
                <p style={{ margin: "0.5rem 0 0 0", color: "#666" }}>
                  Текущее время
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
      {tab === "stats" && (
        <div style={{ maxWidth: "900px", margin: "0 auto" }}>
          <h2 style={{ color: "#333", marginBottom: "1.5rem" }}>Статистика посещаемости</h2>
          {Array.isArray(stats) && stats.length > 0 ? (
            <>
              <div style={{ 
                height: "400px", 
                backgroundColor: "white", 
                padding: "20px", 
                borderRadius: "8px",
                boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
                marginBottom: "2rem"
              }}>
                <Line data={chartData} options={chartOptions} />
              </div>
              
              <div style={{ 
                marginTop: "1.5rem", 
                padding: "1.5rem", 
                backgroundColor: "white", 
                borderRadius: "8px",
                boxShadow: "0 2px 4px rgba(0,0,0,0.1)"
              }}>
                <h3 style={{ margin: "0 0 1rem 0", color: "#333" }}>Сводная информация</h3>
                <div style={{ display: "flex", justifyContent: "center", gap: "2rem", flexWrap: "wrap" }}>
                  <div style={{ 
                    padding: "15px", 
                    backgroundColor: "#f1f3f9", 
                    borderRadius: "8px", 
                    minWidth: "150px" 
                  }}>
                    <p style={{ fontWeight: "bold", fontSize: "28px", margin: "0", color: "#4c6ef5" }}>
                      {stats.length > 0 ? Math.max(...stats.map(s => s.count)) : 0}
                    </p>
                    <p style={{ margin: "0.5rem 0 0 0", color: "#666" }}>
                      Максимальное количество
                    </p>
                  </div>
                  <div style={{ 
                    padding: "15px", 
                    backgroundColor: "#f1f3f9", 
                    borderRadius: "8px", 
                    minWidth: "150px" 
                  }}>
                    <p style={{ fontWeight: "bold", fontSize: "28px", margin: "0", color: "#4c6ef5" }}>
                      {stats.length > 0 ? Math.round(stats.reduce((acc, s) => acc + s.count, 0) / stats.length) : 0}
                    </p>
                    <p style={{ margin: "0.5rem 0 0 0", color: "#666" }}>
                      Среднее количество
                    </p>
                  </div>
                  <div style={{ 
                    padding: "15px", 
                    backgroundColor: "#f1f3f9", 
                    borderRadius: "8px", 
                    minWidth: "150px" 
                  }}>
                    <p style={{ fontWeight: "bold", fontSize: "28px", margin: "0", color: "#4c6ef5" }}>
                      {stats.length > 0 ? stats[0].count : 0}
                    </p>
                    <p style={{ margin: "0.5rem 0 0 0", color: "#666" }}>
                      Последнее измерение
                    </p>
                  </div>
                </div>
              </div>
              
              <div style={{ marginTop: "2rem" }}>
                <h3 style={{ color: "#333", marginBottom: "1rem" }}>История измерений</h3>
                <div style={{ overflowX: "auto" }}>
                  <table style={{ 
                    width: "100%", 
                    borderCollapse: "collapse", 
                    backgroundColor: "white",
                    boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
                    borderRadius: "8px",
                    overflow: "hidden"
                  }}>
                    <thead>
                      <tr style={{ backgroundColor: "#4c6ef5", color: "white" }}>
                        <th style={{ padding: "12px", textAlign: "left" }}>№</th>
                        <th style={{ padding: "12px", textAlign: "left" }}>Дата и время</th>
                        <th style={{ padding: "12px", textAlign: "center" }}>Количество студентов</th>
                      </tr>
                    </thead>
                    <tbody>
                      {stats.map((item, index) => (
                        <tr key={index} style={{ backgroundColor: index % 2 === 0 ? "white" : "#f8f9fa" }}>
                          <td style={{ padding: "10px", borderBottom: "1px solid #eee" }}>{index + 1}</td>
                          <td style={{ padding: "10px", borderBottom: "1px solid #eee" }}>
                            {new Date(item.timestamp).toLocaleString()}
                          </td>
                          <td style={{ 
                            padding: "10px", 
                            textAlign: "center", 
                            borderBottom: "1px solid #eee",
                            fontWeight: "bold",
                            color: item.count > 0 ? "#4c6ef5" : "#888"
                          }}>
                            {item.count}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          ) : (
            <div style={{ 
              padding: "3rem", 
              backgroundColor: "white", 
              borderRadius: "8px",
              boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
              color: "#666",
              textAlign: "center"
            }}>
              <p style={{ fontSize: "18px", marginBottom: "1rem" }}>Нет данных для отображения</p>
              <p>Запустите распознавание в режиме камеры для сбора статистики</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;