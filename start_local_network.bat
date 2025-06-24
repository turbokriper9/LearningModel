@echo off
echo === Запуск системы учета посещаемости в локальной сети ===
echo.

REM Обновление URL API во фронтенде
echo Обновление URL API для локальной сети...
python update_frontend_url.py
echo.

REM Запуск бэкенда
start cmd /k "python run.py"
echo Бэкенд запущен на порту 8000...
echo.

REM Запуск фронтенда
cd frontend
start cmd /k "npm start"
cd ..
echo Фронтенд запущен на порту 3000...
echo.

REM Получение локального IP-адреса
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /r /c:"IPv4"') do (
    set ip=%%a
    goto :break
)
:break
set ip=%ip:~1%
echo Система доступна по следующим адресам:
echo.
echo API: http://%ip%:8000
echo Фронтенд: http://%ip%:3000
echo.
echo Для доступа с других устройств в локальной сети используйте эти URL.
echo.
pause 