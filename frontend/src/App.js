import React, { useEffect, useRef, useState } from "react";
import "./auth.css";
import "./app.css";
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
  // Состояние для авторизации
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  // Проверка авторизации при загрузке
  useEffect(() => {
    const savedAuth = localStorage.getItem("isAuthenticated");
    if (savedAuth === "true") {
      setIsAuthenticated(true);
    }
  }, []);

  // Основное состояние приложения
  const [tab, setTab] = useState("main");
  const [adminTab, setAdminTab] = useState("info"); // Текущая вкладка в панели администратора
  const [teacherTab, setTeacherTab] = useState("attendance"); // Текущая вкладка в панели преподавателя
  const [periodType, setPeriodType] = useState("day"); // Период для графика нагруженности (день, неделя, месяц)
  const [count, setCount] = useState(null);
  const [boxes, setBoxes] = useState([]);
  const [stats, setStats] = useState([]);
  const [dailyStats, setDailyStats] = useState(null);
  const [lessonStats, setLessonStats] = useState(null);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [selectedLessonNumber, setSelectedLessonNumber] = useState(null);
  const [selectedRoom, setSelectedRoom] = useState("");
  const [manualCount, setManualCount] = useState("");
  const [students, setStudents] = useState([
    { id: 1, name: "Маннанов Данил Радикович", present: true },
    { id: 2, name: "Ануфриев Денис Дмитриевич", present: false },
    { id: 3, name: "Исаев Арсений Евгеньевич", present: true },
    { id: 4, name: "Павлова Милана Андреевна", present: false }
  ]);
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

  // Обработчик изменения камеры
  const handleCameraChange = (cameraId) => {
    console.log(`Переключение на камеру ${cameraId}`);
    setSelectedCamera(cameraId);
    
    // Остановка текущего потока
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    
    // Сброс счетчика
    setCount(null);
    setBoxes([]);
  };

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
      const apiUrl = "http://10.241.1.170:8000/api/v1/attendance";
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
          const res = await fetch("http://10.241.1.170:8000/api/v1/detect-image", {
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

  // useEffect для загрузки статистики
  useEffect(() => {
    if (tab !== "stats") return;

    setIsLoading(true);
    setError(null);

    const fetchStats = () => {
      console.log(`Загрузка статистики: дата=${selectedDate}, пара=${selectedLessonNumber}`);
      
      // Формируем URL с параметрами для фильтрации
      let url = "http://10.241.1.170:8000/api/v1/attendance";
      const params = new URLSearchParams();
      
      if (selectedDate) {
        params.append("date", selectedDate);
        console.log(`Добавлен параметр date=${selectedDate}`);
      }
      
      if (selectedLessonNumber !== null) {
        params.append("lesson_number", selectedLessonNumber);
        console.log(`Добавлен параметр lesson_number=${selectedLessonNumber}`);
      }
      
      if (params.toString()) {
        url += `?${params.toString()}`;
      }
      
      console.log(`Запрос к API: ${url}`);
      
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
          setIsLoading(false);
        })
        .catch((error) => {
          console.error("Ошибка при получении статистики:", error);
          setStats([]);
          setError("Ошибка при загрузке данных");
          setIsLoading(false);
        });
        
      // Если выбрана конкретная пара, получаем детальную статистику по ней
      if (selectedLessonNumber !== null) {
        const lessonStatsUrl = `/api/v1/attendance/lesson-stats?lesson_number=${selectedLessonNumber}${selectedDate ? `&date=${selectedDate}` : ''}`;
        console.log(`Запрос статистики по паре: ${lessonStatsUrl}`);
        
        fetch(lessonStatsUrl)
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
        const dailyStatsUrl = `/api/v1/attendance/daily-stats${selectedDate ? `?date=${selectedDate}` : ''}`;
        console.log(`Запрос общей статистики по парам: ${dailyStatsUrl}`);
        
        fetch(dailyStatsUrl)
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
    
    // И обновляем каждые 30 секунд (увеличили интервал для уменьшения нагрузки)
    const interval = setInterval(fetchStats, 30000);
    
    return () => clearInterval(interval);
  }, [tab, selectedDate, selectedLessonNumber]); // Явно указываем зависимости

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

  // Функция для рендеринга статистики
  const renderStats = () => {
    if (isLoading) {
      return <div className="loading">Загрузка данных...</div>;
    }
    
    if (error) {
      return <div className="error">{error}</div>;
    }
    
    if (!stats || stats.length === 0) {
      return <p className="no-data">Нет данных для отображения</p>;
    }

    // Формирование данных для графика
    const chartData = {
      labels: stats.map(item => formatDate(item.timestamp)),
      datasets: [
        {
          label: 'Количество студентов',
          data: stats.map(item => item.count),
          backgroundColor: 'rgba(76, 175, 80, 0.2)',
          borderColor: 'rgba(76, 175, 80, 1)',
          borderWidth: 2,
        }
      ]
    };

    const chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { 
          position: 'top',
        },
        title: { 
          display: true, 
          text: `График посещаемости ${selectedDate ? `за ${selectedDate}` : ''}`
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Количество студентов'
          }
        },
        x: {
          title: {
            display: true,
            text: 'Время'
          }
        }
      }
    };

    return (
      <>
        <div className="chart-container">
          <h2>График посещаемости</h2>
          <Line data={chartData} options={chartOptions} />
        </div>

        {/* Отображаем детальную статистику по конкретной паре */}
        {lessonStats && selectedLessonNumber !== null && (
          <div className="chart-container">
            <h2>Динамика посещаемости {selectedLessonNumber} пары ({lessonStats.lesson_time})</h2>
            <Line 
              data={{
                labels: lessonStats.time_series.map(item => formatDate(item.timestamp)),
                datasets: [
                  {
                    label: 'Количество студентов',
                    data: lessonStats.time_series.map(item => item.count),
                    backgroundColor: 'rgba(33, 150, 243, 0.2)',
                    borderColor: 'rgba(33, 150, 243, 1)',
                    borderWidth: 2,
                    tension: 0.3
                  }
                ]
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'top',
                  },
                  title: {
                    display: true,
                    text: `Максимальное количество: ${lessonStats.max_count} студентов`
                  }
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    title: {
                      display: true,
                      text: 'Количество студентов'
                    }
                  },
                  x: {
                    title: {
                      display: true,
                      text: 'Время'
                    }
                  }
                }
              }}
            />
          </div>
        )}

        {/* Отображаем общую статистику по парам */}
        {dailyStats && selectedLessonNumber === null && (
          <div className="chart-container">
            <h2>Посещаемость по парам</h2>
            <Bar 
              data={{
                labels: Object.keys(dailyStats.attendance || {}).map(key => {
                  const lessonNum = key.replace('lesson_', '');
                  return `${lessonNum} пара (${dailyStats.schedule?.[key] || ''})`;
                }),
                datasets: [
                  {
                    label: 'Макс. количество студентов',
                    data: Object.values(dailyStats.attendance || {}),
                    backgroundColor: 'rgba(76, 175, 80, 0.2)',
                    borderColor: 'rgba(76, 175, 80, 1)',
                    borderWidth: 2,
                  }
                ]
              }}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'top',
                  },
                  title: {
                    display: true,
                    text: `Максимальное количество студентов по парам (${dailyStats.date || 'сегодня'})`
                  }
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    title: {
                      display: true,
                      text: 'Количество студентов'
                    }
                  }
                }
              }}
            />
          </div>
        )}

        <div className="table-container">
          <h2>Таблица посещаемости</h2>
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
        </div>
      </>
    );
  };

  // Компонент экрана авторизации
  const LoginScreen = () => {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [loginError, setLoginError] = useState("");
    
    // Обработчик авторизации
    const handleLogin = (e) => {
      e.preventDefault();
      setLoginError("");
      
      // Проверка логина/пароля
      if (username === "admin" && password === "123456") {
        setIsAuthenticated(true);
        localStorage.setItem("isAuthenticated", "true");
      } else {
        setLoginError("Неверный логин или пароль");
      }
    };
    
    return (
      <div className="auth-container">
        <div className="auth-card">
          <img src="/images/URFU.png" alt="Логотип УрФУ" className="auth-logo" />
          <h2 className="auth-title">Система учета посещаемости</h2>
          
          {loginError && <div className="error-message">{loginError}</div>}
          
          <form onSubmit={handleLogin} className="auth-form">
            <div className="form-group">
              <label htmlFor="username">Логин</label>
              <input
                type="text"
                id="username"
                className="form-control"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="password">Пароль</label>
              <input
                type="password"
                id="password"
                className="form-control"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            
            <button type="submit" className="btn">Войти</button>
          </form>
          
          <div className="auth-hint">
            Подсказка: логин: admin, пароль: 123456
          </div>
        </div>
      </div>
    );
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
      </div>
    );
  };

  // Компонент панели администратора
  const AdminPanel = () => {
    return (
      <div className="admin-panel">
        <div className="admin-nav">
          <button 
            className={adminTab === "info" ? "active" : ""} 
            onClick={() => setAdminTab("info")}
          >
            Информация
          </button>
          <button 
            className={adminTab === "institute-load" ? "active" : ""} 
            onClick={() => setAdminTab("institute-load")}
          >
            Нагруженность ИРИТ-РТФ
          </button>
          <button 
            className={adminTab === "room-load" ? "active" : ""} 
            onClick={() => setAdminTab("room-load")}
          >
            Нагруженность аудиторий
          </button>
        </div>
        
        <div className="admin-content">
          {adminTab === "info" && (
            <div className="admin-info">
              <h2>Информационная панель</h2>
              <div className="info-cards">
                <div className="info-card">
                  <h3>Общая статистика</h3>
                  <div className="info-stat">
                    <span className="stat-label">Всего аудиторий:</span>
                    <span className="stat-value">42</span>
                  </div>
                  <div className="info-stat">
                    <span className="stat-label">Активных камер:</span>
                    <span className="stat-value">{videoDevices.length || 1}</span>
                  </div>
                  <div className="info-stat">
                    <span className="stat-label">Записей в базе:</span>
                    <span className="stat-value">{stats.length || 0}</span>
                  </div>
                </div>
                
                <div className="info-card">
                  <h3>Текущая загруженность</h3>
                  <div className="info-stat highlight">
                    <span className="stat-label">Студентов в аудиториях:</span>
                    <span className="stat-value">{count || "..."}</span>
                  </div>
                  <div className="info-stat">
                    <span className="stat-label">Последнее обновление:</span>
                    <span className="stat-value">{new Date().toLocaleTimeString()}</span>
                  </div>
                </div>
                
                <div className="info-card">
                  <h3>Система</h3>
                  <div className="info-stat">
                    <span className="stat-label">Статус API:</span>
                    <span className="stat-value success">Онлайн</span>
                  </div>
                  <div className="info-stat">
                    <span className="stat-label">Модель ИИ:</span>
                    <span className="stat-value">YOLOv8</span>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {adminTab === "institute-load" && (
            <div className="admin-institute-load">
              <h2>График нагруженности ИРИТ-РТФ</h2>
              
              <div className="period-selector">
                <button 
                  className={periodType === "day" ? "active" : ""} 
                  onClick={() => setPeriodType("day")}
                >
                  День
                </button>
                <button 
                  className={periodType === "week" ? "active" : ""} 
                  onClick={() => setPeriodType("week")}
                >
                  Неделя
                </button>
                <button 
                  className={periodType === "month" ? "active" : ""} 
                  onClick={() => setPeriodType("month")}
                >
                  Месяц
                </button>
              </div>
              
              <div className="chart-container">
                {periodType === "day" && (
                  <Line 
                    data={{
                      labels: ["8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00"],
                      datasets: [
                        {
                          label: 'Количество студентов',
                          data: [10, 120, 180, 210, 190, 150, 210, 250, 220, 180, 130, 90, 40],
                          backgroundColor: 'rgba(33, 150, 243, 0.2)',
                          borderColor: 'rgba(33, 150, 243, 1)',
                          borderWidth: 2,
                          tension: 0.3
                        }
                      ]
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: 'top',
                        },
                        title: {
                          display: true,
                          text: `Нагруженность ИРИТ-РТФ за ${selectedDate}`
                        }
                      },
                      scales: {
                        y: {
                          beginAtZero: true,
                          title: {
                            display: true,
                            text: 'Количество студентов'
                          }
                        },
                        x: {
                          title: {
                            display: true,
                            text: 'Время'
                          }
                        }
                      }
                    }}
                  />
                )}
                
                {periodType === "week" && (
                  <Line 
                    data={{
                      labels: ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"],
                      datasets: [
                        {
                          label: 'Средняя нагруженность',
                          data: [180, 210, 190, 220, 170, 120],
                          backgroundColor: 'rgba(156, 39, 176, 0.2)',
                          borderColor: 'rgba(156, 39, 176, 1)',
                          borderWidth: 2,
                          tension: 0.3
                        },
                        {
                          label: 'Максимальная нагруженность',
                          data: [250, 280, 260, 290, 240, 180],
                          backgroundColor: 'rgba(233, 30, 99, 0.2)',
                          borderColor: 'rgba(233, 30, 99, 1)',
                          borderWidth: 2,
                          tension: 0.3
                        }
                      ]
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: 'top',
                        },
                        title: {
                          display: true,
                          text: 'Нагруженность ИРИТ-РТФ по дням недели'
                        }
                      },
                      scales: {
                        y: {
                          beginAtZero: true,
                          title: {
                            display: true,
                            text: 'Количество студентов'
                          }
                        }
                      }
                    }}
                  />
                )}
                
                {periodType === "month" && (
                  <Bar
                    data={{
                      labels: ["Неделя 1", "Неделя 2", "Неделя 3", "Неделя 4"],
                      datasets: [
                        {
                          label: 'Средняя нагруженность',
                          data: [190, 200, 210, 180],
                          backgroundColor: 'rgba(0, 150, 136, 0.2)',
                          borderColor: 'rgba(0, 150, 136, 1)',
                          borderWidth: 2
                        },
                        {
                          label: 'Пиковая нагруженность',
                          data: [270, 290, 300, 260],
                          backgroundColor: 'rgba(255, 87, 34, 0.2)',
                          borderColor: 'rgba(255, 87, 34, 1)',
                          borderWidth: 2
                        }
                      ]
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: {
                        legend: {
                          position: 'top',
                        },
                        title: {
                          display: true,
                          text: 'Нагруженность ИРИТ-РТФ по неделям'
                        }
                      },
                      scales: {
                        y: {
                          beginAtZero: true,
                          title: {
                            display: true,
                            text: 'Количество студентов'
                          }
                        }
                      }
                    }}
                  />
                )}
              </div>
            </div>
          )}
          
          {adminTab === "room-load" && (
            <div className="admin-room-load">
              <h2>График нагруженности аудиторий</h2>
              
              <div className="chart-container">
                <Bar
                  data={{
                    labels: ["Р-237", "Р-239", "Р-241", "Р-243", "Р-245", "Р-247", "Р-249", "Р-251"],
                    datasets: [
                      {
                        label: 'Средняя заполненность (%)',
                        data: [85, 70, 90, 65, 75, 80, 60, 95],
                        backgroundColor: 'rgba(76, 175, 80, 0.2)',
                        borderColor: 'rgba(76, 175, 80, 1)',
                        borderWidth: 2
                      }
                    ]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'top',
                      },
                      title: {
                        display: true,
                        text: 'Средняя заполненность аудиторий'
                      }
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                          display: true,
                          text: 'Заполненность (%)'
                        }
                      }
                    }
                  }}
                />
              </div>
              
              <div className="chart-container">
                <Line
                  data={{
                    labels: ["8:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"],
                    datasets: [
                      {
                        label: 'Р-237',
                        data: [10, 85, 90, 80, 85, 70, 20],
                        borderColor: 'rgba(33, 150, 243, 1)',
                        backgroundColor: 'rgba(33, 150, 243, 0.1)',
                        tension: 0.3
                      },
                      {
                        label: 'Р-239',
                        data: [5, 70, 75, 65, 80, 60, 10],
                        borderColor: 'rgba(156, 39, 176, 1)',
                        backgroundColor: 'rgba(156, 39, 176, 0.1)',
                        tension: 0.3
                      },
                      {
                        label: 'Р-241',
                        data: [15, 90, 95, 85, 90, 75, 25],
                        borderColor: 'rgba(76, 175, 80, 1)',
                        backgroundColor: 'rgba(76, 175, 80, 0.1)',
                        tension: 0.3
                      }
                    ]
                  }}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        position: 'top',
                      },
                      title: {
                        display: true,
                        text: 'Динамика заполненности аудиторий в течение дня'
                      }
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                          display: true,
                          text: 'Заполненность (%)'
                        }
                      },
                      x: {
                        title: {
                          display: true,
                          text: 'Время'
                        }
                      }
                    }
                  }}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  // Компонент панели преподавателя
  const TeacherPanel = () => {
    // Обработчик изменения статуса присутствия студента
    const handleTogglePresence = (studentId) => {
      setStudents(students.map(student => 
        student.id === studentId 
          ? { ...student, present: !student.present } 
          : student
      ));
    };

    // Обработчик сохранения данных о посещаемости
    const handleSaveAttendance = (e) => {
      e.preventDefault();
      
      // Проверка заполнения обязательных полей
      if (!selectedLessonNumber || !selectedRoom) {
        alert("Пожалуйста, выберите пару и аудиторию");
        return;
      }
      
      // Подготовка данных для отправки
      const attendanceData = {
        lesson_number: selectedLessonNumber,
        room: selectedRoom,
        count: parseInt(manualCount) || 0,
        date: selectedDate,
        students: students.map(student => ({
          id: student.id,
          name: student.name,
          present: student.present
        }))
      };
      
      // Здесь будет отправка данных на сервер
      console.log("Отправка данных о посещаемости:", attendanceData);
      
      // Имитация успешного сохранения
      setSavingStatus('success');
      setTimeout(() => {
        setSavingStatus(null);
      }, 3000);
    };

    return (
      <div className="teacher-panel">
        <div className="teacher-nav">
          <button 
            className={teacherTab === "attendance" ? "active" : ""} 
            onClick={() => setTeacherTab("attendance")}
          >
            Отметка посещаемости
          </button>
          <button 
            className={teacherTab === "students" ? "active" : ""} 
            onClick={() => setTeacherTab("students")}
          >
            Список студентов
          </button>
        </div>
        
        <div className="teacher-content">
          {teacherTab === "attendance" && (
            <div className="manual-attendance">
              <h2>Ручная отметка посещаемости</h2>
              
              <form onSubmit={handleSaveAttendance} className="attendance-form">
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="lesson-select">Пара:</label>
                    <select 
                      id="lesson-select" 
                      value={selectedLessonNumber === null ? '' : selectedLessonNumber}
                      onChange={(e) => setSelectedLessonNumber(e.target.value === '' ? null : Number(e.target.value))}
                      required
                    >
                      <option value="">Выберите пару</option>
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
                  
                  <div className="form-group">
                    <label htmlFor="room-select">Аудитория:</label>
                    <select 
                      id="room-select" 
                      value={selectedRoom}
                      onChange={(e) => setSelectedRoom(e.target.value)}
                      required
                    >
                      <option value="">Выберите аудиторию</option>
                      <option value="Р-237">Р-237</option>
                      <option value="Р-239">Р-239</option>
                      <option value="Р-241">Р-241</option>
                      <option value="Р-243">Р-243</option>
                      <option value="Р-245">Р-245</option>
                      <option value="Р-247">Р-247</option>
                      <option value="Р-249">Р-249</option>
                      <option value="Р-251">Р-251</option>
                    </select>
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="date-select">Дата:</label>
                    <input 
                      type="date" 
                      id="date-select" 
                      value={selectedDate}
                      onChange={(e) => setSelectedDate(e.target.value)}
                      required
                    />
                  </div>
                </div>
                
                <div className="form-group">
                  <label htmlFor="manual-count">Количество студентов:</label>
                  <input 
                    type="number" 
                    id="manual-count" 
                    min="0"
                    value={manualCount}
                    onChange={(e) => setManualCount(e.target.value)}
                    placeholder="Введите количество студентов"
                  />
                </div>
                
                <div className="student-list-container">
                  <h3>Список студентов</h3>
                  <table className="student-table">
                    <thead>
                      <tr>
                        <th>№</th>
                        <th>ФИО</th>
                        <th>Статус</th>
                        <th>Действие</th>
                      </tr>
                    </thead>
                    <tbody>
                      {students.map((student, index) => (
                        <tr key={student.id} className={student.present ? "present" : "absent"}>
                          <td>{index + 1}</td>
                          <td>{student.name}</td>
                          <td>{student.present ? "Присутствует" : "Отсутствует"}</td>
                          <td>
                            <button 
                              type="button"
                              className={`toggle-btn ${student.present ? "present" : "absent"}`}
                              onClick={() => handleTogglePresence(student.id)}
                            >
                              {student.present ? "Отметить отсутствие" : "Отметить присутствие"}
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                
                <div className="form-actions">
                  <button type="submit" className="save-btn">Сохранить</button>
                  {savingStatus === 'success' && (
                    <span className="save-status success">Данные успешно сохранены</span>
                  )}
                </div>
              </form>
            </div>
          )}
          
          {teacherTab === "students" && (
            <div className="students-list">
              <h2>Список студентов</h2>
              
              <div className="search-container">
                <input 
                  type="text" 
                  placeholder="Поиск по имени..." 
                  className="search-input"
                />
              </div>
              
              <table className="student-table full-list">
                <thead>
                  <tr>
                    <th>№</th>
                    <th>ФИО</th>
                    <th>Группа</th>
                    <th>Посещаемость</th>
                  </tr>
                </thead>
                <tbody>
                  {students.map((student, index) => (
                    <tr key={student.id}>
                      <td>{index + 1}</td>
                      <td>{student.name}</td>
                      <td>РИ-380022</td>
                      <td>{student.present ? "85%" : "70%"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div>
      {!isAuthenticated ? (
        <LoginScreen />
      ) : (
    <div className="app">
      <header>
        <h1>
          <img src="/images/URFU.png" alt="УрФУ" className="logo" />
          Система подсчета студентов
        </h1>
        <div className="tabs">
              <button className={tab === "main" ? "active" : ""} onClick={() => setTab("main")}>Камера</button>
              <button className={tab === "stats" ? "active" : ""} onClick={() => setTab("stats")}>Статистика</button>
              <button className={tab === "admin" ? "active" : ""} onClick={() => setTab("admin")}>Панель администратора</button>
              <button className={tab === "teacher" ? "active" : ""} onClick={() => setTab("teacher")}>Панель преподавателя</button>
              <button onClick={() => {
                setIsAuthenticated(false);
                localStorage.removeItem("isAuthenticated");
              }}>Выйти</button>
      </div>
      </header>

      <main>
            <div id="main-tab" className="tab-content" style={{ display: tab === "main" ? "block" : "none" }}>
              {/* Содержимое вкладки "Камера" */}
            <div className="camera-container">
              <div className="video-wrapper">
                  <video ref={videoRef} autoPlay playsInline muted></video>
                  <canvas ref={canvasRef} className="detection-canvas"></canvas>
                </div>
                
                <div className="detection-info">
                  <div className="count">
                    <span className="count-number">{count !== null ? count : "..."}</span>
                    <span className="count-label">студентов</span>
                    <div className="save-info">
                      {savingStatus === 'saving' && (
                        <span className="save-status">Сохранение...</span>
                      )}
                      {savingStatus === 'success' && (
                        <span className="save-status success">Данные сохранены</span>
                      )}
                      {savingStatus === 'error' && (
                        <span className="save-status error">Ошибка сохранения: {saveError}</span>
                      )}
                      <span className="save-hint">
                        Данные сохраняются автоматически каждые 5 минут
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              
              <CameraSelector />
            </div>
            
            <div id="stats-tab" className="tab-content" style={{ display: tab === "stats" ? "block" : "none" }}>
              {/* Содержимое вкладки "Статистика" */}
              <StatsFilters />
              
                {isLoading ? (
                <div className="loading">Загрузка данных...</div>
                ) : error ? (
                  <div className="error">{error}</div>
              ) : (
                <div className="stats-content">
                  {/* Графики и статистика */}
                  {renderStats()}
                </div>
              )}
            </div>
            
            <div id="admin-tab" className="tab-content" style={{ display: tab === "admin" ? "block" : "none" }}>
              {/* Содержимое вкладки "Панель администратора" */}
              <AdminPanel />
            </div>
            
            <div id="teacher-tab" className="tab-content" style={{ display: tab === "teacher" ? "block" : "none" }}>
              {/* Содержимое вкладки "Панель преподавателя" */}
              <TeacherPanel />
            </div>
          </main>
        </div>
      )}
    </div>
  );
}

export default App;