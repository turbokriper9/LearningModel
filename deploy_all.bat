@echo off
echo ===============================================
echo    ПУБЛИКАЦИЯ СИСТЕМЫ УЧЕТА ПОСЕЩАЕМОСТИ
echo ===============================================
echo.
echo Этот скрипт позволяет выбрать способ публикации вашего приложения
echo в интернете для доступа из любой точки мира.
echo.
echo Доступные варианты:
echo.
echo 1. Полная версия на PythonAnywhere (с бэкендом)
echo 2. Статическая версия на GitHub Pages
echo 3. Статическая версия на Netlify (самый простой вариант)
echo 4. Открыть описание всех способов публикации
echo 5. Выход
echo.

set /p choice=Введите номер выбранного варианта (1-5): 

if "%choice%"=="1" (
    start deploy_web.bat
) else if "%choice%"=="2" (
    start deploy_static.bat
) else if "%choice%"=="3" (
    start deploy_netlify.bat
) else if "%choice%"=="4" (
    start "" global_readme.md
) else if "%choice%"=="5" (
    exit
) else (
    echo.
    echo Неверный выбор. Пожалуйста, выберите число от 1 до 5.
    echo.
    pause
    deploy_all.bat
) 