@echo off
cd /d "%~dp0"
set PYTHONPATH=src
python src/app/main.py
if errorlevel 1 (
    echo.
    echo Une erreur s'est produite. Voir logs\app.log pour les details.
    pause
)
