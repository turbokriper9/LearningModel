import React, { useEffect, useRef, useState } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Line, Bar } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function App() {
  const [tab, setTab] = useState("main");
  const [count, setCount] = useState(null);
  const [boxes, setBoxes] = useState([]);
  const [stats, setStats] = useState([]);
  const [dailyStats, setDailyStats] = useState(null);
  const [lessonStats, setLessonStats] = useState(null);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [selectedLessonNumber, setSelectedLessonNumber] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [availableCameras, setAvailableCameras] = useState([]);
  const [selectedCamera, setSelectedCamera] = useState(0);
  const [videoDevices, setVideoDevices] = useState([]);
  const [lastSavedCount, setLastSavedCount] = useState(null);
  const [saveInterval, setSaveInterval] = useState(null);
  const [savingStatus, setSavingStatus] = useState(null); // 'saving', 'success', 'error'
  const [saveError, setSaveError] = useState(null);
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

  // Функция для сохранения данных о количестве студентов в базу данных
  const saveAttendanceData = async () => {
    // Не сохраняем, если счетчик равен 0, null или такое же значение уже сохранено
    if (count === null || count <= 0 || count === lastSavedCount) return;
    
    try {
      setSavingStatus('saving');
      setSaveError(null);
      
      // Подготавливаем данные согласно схеме API
      const attendanceData = {
        count: count,
        // lesson_number определяется на сервере автоматически, если не указано
      };
      
      console.log("Отправляемые данные:", attendanceData);
      
      // Используем полный URL API
      const apiUrl = "http://10.14.24.35:8000/api/v1/attendance";
      console.log("Отправка данных на:", apiUrl);
      
      const response = await fetch(apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify(attendanceData),
      });
      
      console.log("Статус ответа:", response.status, response.statusText);
      
      if (response.ok) {
        const responseData = await response.json();
        console.log("Данные успешно сохранены в базу данных:", responseData);
        setLastSavedCount(count);
        setSavingStatus('success');
        
        // Сбросить статус через 2 секунды
        setTimeout(() => {
          setSavingStatus(null);
        }, 2000);
      } else {
        console.log("Получен ответ с ошибкой:", response);
        // Пробуем прочитать текст ошибки
        const responseText = await response.text();
        console.error("Текст ошибки:", responseText);
        
        let errorDetail = "Неизвестная ошибка";
        try {
          // Если ответ содержит JSON, парсим его
          if (responseText && responseText.trim().startsWith('{')) {
            const errorData = JSON.parse(responseText);
            errorDetail = errorData.detail || response.statusText || 'Неизвестная ошибка';
          } else {
            errorDetail = response.statusText || responseText || 'Ошибка соединения с сервером';
          }
        } catch (parseError) {
          console.error("Ошибка парсинга JSON:", parseError);
          errorDetail = responseText || response.statusText || 'Ошибка формата ответа сервера';
        }
        
        setSavingStatus('error');
        setSaveError(`Ошибка сохранения: ${errorDetail}`);
      }
    } catch (error) {
      console.error("Ошибка запроса:", error);
      setSavingStatus('error');
      setSaveError(`Ошибка запроса: ${error.message || 'Не удалось соединиться с сервером'}`);
    }
  };

  // Настройка автоматического сохранения данных каждые 5 секунд
  useEffect(() => {
    if (tab === "main") {
      // Запускаем интервал для сохранения данных
      const intervalId = setInterval(() => {
        if (count !== null) {
          saveAttendanceData();
        }
      }, 5000); // 5000 мс = 5 секунд
      
      setSaveInterval(intervalId);
      
      return () => {
        // Очищаем интервал при размонтировании компонента или смене вкладки
        clearInterval(intervalId);
        setSaveInterval(null);
      };
    } else if (saveInterval) {
      // Останавливаем интервал при переключении вкладки
      clearInterval(saveInterval);
      setSaveInterval(null);
    }
  }, [tab, count]);

  // Обработчик переключения камеры
  const handleCameraChange = (cameraId) => {
    console.log(`Переключение на камеру ${cameraId}`);
    setSelectedCamera(cameraId);
    setError(null);
    setBoxes([]);
    setCount(null);
    setLastSavedCount(null); // Сбрасываем сохраненное значение при смене камеры
  };

  // Детекция людей каждую секунду
  useEffect(() => {
    if (tab !== "main") return;
    
    let errorCount = 0; // Счетчик последовательных ошибок
    const maxErrorCount = 3; // Максимальное количество ошибок подряд перед сбросом счетчика
    
    const detect = async () => {
      try {
        const video = videoRef.current;
        if (!video || !video.videoWidth || !video.videoHeight) return;
        
        setError(null);
        
        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext("2d");
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL("image/jpeg");
        
        console.log("Отправка запроса на обнаружение...");
        
        // Устанавливаем таймаут для запроса
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 секунд таймаут
        
        try {
          const res = await fetch("http://10.14.24.35:8000/api/v1/detect-image", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image: dataUrl }),
            signal: controller.signal
          });
          
          clearTimeout(timeoutId); // Очищаем таймаут после успешного ответа
          
          if (!res.ok) {
            throw new Error(`Ошибка запроса: ${res.status}`);
          }
          
          const data = await res.json();
          console.log("Получен ответ:", data);
          
          // Сбрасываем счетчик ошибок после успешного запроса
          errorCount = 0;
          
          // Вводим сглаживание - обновляем счетчик, только если разница значительная
          const newCount = data.count;
          
          // Всегда обновляем счетчик, если вернулся положительный результат
          if (newCount > 0) {
            setCount(newCount);
            console.log("Обновлен счетчик:", newCount);
          } else {
            // Устанавливаем 0 только если счетчик еще не инициализирован
            if (count === null) {
              setCount(0);
              console.log("Инициализирован счетчик значением 0");
            } else {
              // Если предыдущее значение != 0, постепенно уменьшаем до 0
              if (count > 0) {
                setCount(prevCount => Math.max(0, prevCount - 1));
                console.log("Постепенное уменьшение счетчика:", Math.max(0, count - 1));
              }
            }
          }
          
          setBoxes(data.boxes || []);
          if (data.error) {
            setError(data.error);
          }
        } catch (fetchError) {
          clearTimeout(timeoutId);
          throw fetchError; // Пробрасываем ошибку для обработки в блоке catch снаружи
        }
      } catch (e) {
        console.error("Ошибка при распознавании:", e);
        
        // Увеличиваем счетчик ошибок
        errorCount++;
        
        if (errorCount >= maxErrorCount) {
          // Если было несколько ошибок подряд, показываем сообщение и сбрасываем счетчик до 0
          setError(`Ошибка соединения с сервером. Попытка восстановления...`);
          if (count !== 0) {
            setCount(0);
          }
        } else {
          // При первых нескольких ошибках сохраняем текущее значение счетчика
          setError(`Ошибка распознавания. Попытка: ${errorCount}/${maxErrorCount}`);
        }
        
        setBoxes([]);
      } finally {
        // Уменьшаем интервал между распознаваниями до 0.5 секунды
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
        // Формируем URL с параметрами для фильтрации
        let url = "http://10.14.24.35:8000/api/v1/attendance";
        const params = new URLSearchParams();
        
        if (selectedDate) {
          params.append("date", selectedDate);
        }
        
        if (selectedLessonNumber !== null) {
          params.append("lesson_number", selectedLessonNumber);
        }
        
        if (params.toString()) {
          url += `?${params.toString()}`;
        }
        
        fetch(url)
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
          
        // Если выбрана конкретная пара, получаем детальную статистику по ней
        if (selectedLessonNumber !== null) {
          fetch(`http://10.14.24.35:8000/api/v1/attendance/lesson-stats?lesson_number=${selectedLessonNumber}${selectedDate ? `&date=${selectedDate}` : ''}`)
            .then((res) => res.json())
            .then((data) => {
              console.log("Получены данные статистики по паре:", data);
              setLessonStats(data);
            })
            .catch((error) => {
              console.error("Ошибка при получении статистики по паре:", error);
              setLessonStats(null);
            });
        } else {
          // Если выбраны "Все пары", получаем общую статистику по парам
          fetch(`http://10.14.24.35:8000/api/v1/attendance/daily-stats${selectedDate ? `?date=${selectedDate}` : ''}`)
            .then((res) => res.json())
            .then((data) => {
              console.log("Получены данные статистики по парам:", data);
              setDailyStats(data);
            })
            .catch((error) => {
              console.error("Ошибка при получении статистики по парам:", error);
              setDailyStats(null);
            });
        }
      };
      
      // Загружаем статистику сразу
      fetchStats();
      
      // И обновляем каждые 10 секунд
      const interval = setInterval(fetchStats, 10000);
      
      return () => clearInterval(interval);
    }
  }, [tab, selectedDate, selectedLessonNumber]);

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

  // Подготовка данных для графика посещаемости по парам
  const lessonChartData = dailyStats ? {
    labels: Object.keys(dailyStats.schedule).map(key => {
      const lessonNum = key.split('_')[1];
      return `${lessonNum} пара (${dailyStats.schedule[key]})`;
    }),
    datasets: [
      {
        label: "Максимальное количество студентов",
        data: Object.keys(dailyStats.attendance).map(key => dailyStats.attendance[key]),
        backgroundColor: "rgba(54, 162, 235, 0.6)",
        borderColor: "rgb(54, 162, 235)",
        borderWidth: 1,
      },
    ],
  } : null;

  // Подготовка данных для графика детальной статистики по конкретной паре
  const lessonDetailChartData = lessonStats ? {
    labels: lessonStats.time_series.map(item => formatDate(item.timestamp)),
    datasets: [
      {
        label: "Количество студентов",
        data: lessonStats.time_series.map(item => item.count),
        fill: false,
        borderColor: "rgb(255, 99, 132)",
        tension: 0.4,
        backgroundColor: "rgba(255, 99, 132, 0.5)",
        pointRadius: 5,
        pointHoverRadius: 7,
        pointBackgroundColor: "rgb(255, 99, 132)",
        pointBorderColor: "#fff",
      },
      {
        label: "Максимальное количество",
        data: lessonStats.time_series.map(() => lessonStats.max_count),
        fill: false,
        borderColor: "rgba(54, 162, 235, 0.6)",
        borderDash: [5, 5],
        pointRadius: 0,
        tension: 0.4,
      }
    ],
  } : null;

  // Опции для графика посещаемости по парам
  const lessonChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "top",
      },
      title: {
        display: true,
        text: `Посещаемость по парам на ${selectedDate || 'сегодня'}`,
        font: {
          size: 18,
          weight: "bold"
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1,
          precision: 0,
        },
        title: {
          display: true,
          text: "Количество студентов",
        },
      },
      x: {
        ticks: {
          maxRotation: 45,
          minRotation: 45,
        },
      },
    },
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

  // Компонент фильтров для статистики
  const StatsFilters = () => {
    return (
      <div className="stats-filters">
        <div className="filter-item">
          <label htmlFor="date-filter">Дата:</label>
          <input
            type="date"
            id="date-filter"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
          />
        </div>
        
        <div className="filter-item">
          <label htmlFor="lesson-filter">Пара:</label>
          <select
            id="lesson-filter"
            value={selectedLessonNumber === null ? '' : selectedLessonNumber}
            onChange={(e) => setSelectedLessonNumber(e.target.value === '' ? null : Number(e.target.value))}
          >
            <option value="">Все пары (общая статистика)</option>
            <option value="1">1 пара (8:30-10:00)</option>
            <option value="2">2 пара (10:15-11:45)</option>
            <option value="3">3 пара (12:00-13:30)</option>
            <option value="4">4 пара (14:15-15:45)</option>
            <option value="5">5 пара (16:00-17:30)</option>
            <option value="6">6 пара (17:40-19:10)</option>
            <option value="7">7 пара (19:15-20:45)</option>
            <option value="8">8 пара (20:50-22:20)</option>
          </select>
        </div>
        
        <div className="filter-info">
          {selectedLessonNumber === null ? (
            <span className="filter-hint">
              <i className="info-icon">ℹ️</i> Отображается статистика по всем парам
            </span>
          ) : (
            <span className="filter-hint">
              <i className="info-icon">ℹ️</i> Отображается детальная статистика по {selectedLessonNumber} паре
            </span>
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
                {error ? (
                  <div className="error">{error}</div>
                ) : (
                  <div className="count">
                    <span className="count-number">{count !== null ? Math.round(count) : '...'}</span>
                    <span className="count-label">
                      {count === null ? 'ожидание' :
                        Math.round(count) === 1 ? "студент" :
                        Math.round(count) >= 2 && Math.round(count) <= 4 ? "студента" :
                        "студентов"
                      }
                    </span>
                    <div className="save-info">
                      {savingStatus === 'saving' ? (
                        <span className="save-status saving">
                          Сохранение данных...
                        </span>
                      ) : savingStatus === 'error' ? (
                        <span className="save-status error">
                          {saveError || "Ошибка сохранения"}
                        </span>
                      ) : lastSavedCount !== null ? (
                        <span className="save-status success">
                          Последнее сохранение: {lastSavedCount} {
                            Math.round(lastSavedCount) === 1
                            ? "студент"
                            : Math.round(lastSavedCount) >= 2 && Math.round(lastSavedCount) <= 4
                            ? "студента"
                            : "студентов"
                          }
                        </span>
                      ) : (
                        <span className="save-status pending">
                          Ожидание первого сохранения...
                        </span>
                      )}
                      <span className="save-hint">
                        Данные автоматически сохраняются каждые 5 секунд
                      </span>
                      <button 
                        className="manual-save-btn"
                        onClick={saveAttendanceData}
                        disabled={savingStatus === 'saving'}
                      >
                        {savingStatus === 'saving' ? 'Сохранение...' : 'Сохранить сейчас'}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="stats-tab">
            <StatsFilters />
            
            <div className="chart-container">
              <h2>График посещаемости</h2>
              {stats.length > 0 ? (
                <Line
                  data={chartData}
                  options={chartOptions}
                />
              ) : (
                <p className="no-data">Нет данных для отображения</p>
              )}
            </div>

            {selectedLessonNumber !== null && lessonStats ? (
              <div className="chart-container">
                <h2>
                  Статистика {selectedLessonNumber} пары ({lessonStats.lesson_time})
                  {lessonStats.max_count > 0 && (
                    <span className="max-count-badge">
                      Макс. количество: {lessonStats.max_count}
                    </span>
                  )}
                </h2>
                {lessonStats.time_series.length > 0 ? (
                  <Line 
                    data={lessonDetailChartData} 
                    options={{
                      ...chartOptions,
                      plugins: {
                        ...chartOptions.plugins,
                        title: {
                          ...chartOptions.plugins.title,
                          text: `Динамика посещаемости ${selectedLessonNumber} пары (${lessonStats.lesson_time})`
                        }
                      }
                    }} 
                  />
                ) : (
                  <p className="no-data">Нет данных для отображения</p>
                )}
              </div>
            ) : (
              <div className="chart-container">
                <h2>Посещаемость по парам</h2>
                {dailyStats ? (
                  <Bar 
                    data={lessonChartData} 
                    options={lessonChartOptions} 
                  />
                ) : (
                  <p className="no-data">Нет данных для отображения</p>
                )}
              </div>
            )}

            <div className="table-container">
              <h2>Таблица посещаемости</h2>
              {stats.length > 0 ? (
                <table className="stats-table">
                  <thead>
                    <tr>
                      <th>Время</th>
                      <th>Пара</th>
                      <th>Количество студентов</th>
                    </tr>
                  </thead>
                  <tbody>
                    {stats.map((item, index) => (
                      <tr key={index}>
                        <td>{formatDate(item.timestamp)}</td>
                        <td>{item.lesson_number ? `${item.lesson_number} пара` : '-'}</td>
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
          min-height: 200px; /* Фиксированная минимальная высота блока */
          background-color: #f8f8f8;
          border-radius: 15px;
          padding: 20px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
          margin-top: 20px;
          width: 100%;
          max-width: 400px;
          margin: 0 auto;
        }
        
        .count-number {
          font-size: 72px;
          font-weight: bold;
          color: #4CAF50;
          transition: all 0.5s ease-in-out;
          min-width: 150px;
          min-height: 90px; /* Фиксированная минимальная высота для цифры */
          text-align: center;
          display: flex;
          align-items: center;
          justify-content: center;
          animation: fadeNumber 0.5s ease-out;
          margin: 10px 0;
          border-radius: 20px;
          background-color: rgba(76, 175, 80, 0.1);
          padding: 15px 25px;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        @keyframes fadeNumber {
          from { opacity: 0.5; transform: scale(0.95); }
          to { opacity: 1; transform: scale(1); }
        }
        
        .count-label {
          font-size: 28px;
          color: #666;
          margin-bottom: 20px;
          transition: color 0.5s ease-in-out;
          min-width: 180px;
          min-height: 40px; /* Фиксированная минимальная высота для подписи */
          text-align: center;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .save-info {
          margin-top: 15px;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 8px;
          background-color: #f9f9f9;
          padding: 15px;
          border-radius: 10px;
          width: 100%;
          max-width: 300px;
          border: 1px solid #eee;
        }
        
        .save-status {
          font-size: 14px;
          font-weight: 500;
          transition: opacity 0.3s ease;
        }
        
        .save-status.success {
          color: #2e7d32;
        }
        
        .save-status.saving {
          color: #1976d2;
        }
        
        .save-status.error {
          color: #d32f2f;
        }
        
        .save-status.pending {
          color: #f57c00;
        }
        
        .save-hint {
          font-size: 12px;
          color: #757575;
          font-style: italic;
          margin-bottom: 8px;
        }
        
        .manual-save-btn {
          padding: 6px 12px;
          background-color: #4CAF50;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 14px;
          transition: all 0.2s;
        }
        
        .manual-save-btn:hover {
          background-color: #3e8e41;
        }
        
        .manual-save-btn:disabled {
          background-color: #cccccc;
          cursor: not-allowed;
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
        
        .stats-filters {
          grid-column: 1 / -1;
          display: flex;
          gap: 20px;
          flex-wrap: wrap;
          background-color: #f5f5f5;
          padding: 15px;
          border-radius: 8px;
          margin-bottom: 10px;
        }
        
        .filter-item {
          display: flex;
          flex-direction: column;
          gap: 5px;
        }
        
        .filter-item label {
          font-weight: bold;
          font-size: 14px;
        }
        
        .filter-item input, .filter-item select {
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
          background-color: white;
        }
        
        .filter-info {
          grid-column: 1 / -1;
          margin-top: 10px;
          text-align: center;
        }
        
        .filter-hint {
          font-size: 13px;
          color: #555;
          background-color: #f5f5f5;
          padding: 5px 10px;
          border-radius: 4px;
          display: inline-block;
        }
        
        .info-icon {
          margin-right: 5px;
          font-style: normal;
        }
        
        .chart-container, .table-container {
          background-color: white;
          border-radius: 8px;
          padding: 20px;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
          height: 400px;
          overflow: auto;
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
        
        .max-count-badge {
          display: inline-block;
          margin-left: 15px;
          padding: 5px 10px;
          background-color: #4CAF50;
          color: white;
          border-radius: 15px;
          font-size: 14px;
          font-weight: normal;
        }
      `}</style>
    </div>
  );
}

export default App;