@echo off
echo Установка зависимостей...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Ошибка при установке зависимостей!
    pause
    exit /b %errorlevel%
)
echo Запуск игры...
python main.py
pause
