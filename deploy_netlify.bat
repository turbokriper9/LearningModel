@echo off
echo === Подготовка к размещению на Netlify ===
echo.
echo Netlify - это простой и быстрый хостинг, который позволяет
echo разместить сайт в интернете буквально за пару минут.
echo.
echo Процесс включает:
echo 1. Создание статических файлов для загрузки
echo 2. Упаковку файлов в ZIP-архив
echo 3. Загрузку архива на Netlify через веб-интерфейс
echo.
echo После выполнения шагов, ваш сайт будет доступен по адресу:
echo https://ИМЯ-САЙТА.netlify.app
echo.
echo Продолжить? (Нажмите Enter)
pause > nul

python deploy_to_netlify.py
pause 