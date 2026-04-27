@echo off
echo ============================================================
echo   KrosDownloadManager - Build Portable .exe
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado. Instala Python 3.9+ desde python.org
    pause
    exit /b 1
)

REM Install dependencies
echo Instalando dependencias...
pip install -e ".[build]" --quiet

echo.
echo Construyendo ejecutable portable...
python build.py

echo.
pause
