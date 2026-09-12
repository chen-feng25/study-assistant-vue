@echo off
cd /d "%~dp0"

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found! Please install Python 3.9+
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

python -c "import fastapi" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Failed. Run: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo   Study Assistant - Starting...
echo   http://127.0.0.1:8501
echo ========================================
echo.

python server.py
pause
