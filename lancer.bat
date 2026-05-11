@echo off
cd /d "%~dp0"

:: Lancer AHK directement — garanti de fonctionner
set AHK_EXE=C:\Program Files\AutoHotkey\v1.1.37.02\AutoHotkeyU64.exe
set AHK_SCRIPT=%~dp0data_local\RevitMacros.ahk

if exist "%AHK_EXE%" (
    start "" "%AHK_EXE%" "%AHK_SCRIPT%"
) else (
    echo AutoHotkey introuvable : %AHK_EXE%
)

set PYTHONPATH=src
python src/app/main.py
if errorlevel 1 (
    echo.
    echo Une erreur s'est produite. Voir logs\app.log pour les details.
    pause
)
