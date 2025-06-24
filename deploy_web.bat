@echo off
echo === Подготовка приложения к размещению в интернете ===
echo.
echo Этот скрипт подготовит ваше приложение для размещения на PythonAnywhere,
echo что даст доступ к вашему сайту из любой точки мира через интернет.
echo.
echo Процесс включает:
echo 1. Создание архива с вашим приложением
echo 2. Генерацию инструкций по развертыванию
echo 3. Открытие сайта регистрации на PythonAnywhere
echo.
echo После выполнения шагов, ваш сайт будет доступен по адресу:
echo https://ВАШ_ЛОГИН.pythonanywhere.com
echo.
echo Продолжить? (Нажмите Enter)
pause > nul

python deploy_pythonanywhere.py
pause 