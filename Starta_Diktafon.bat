@echo off
cd /d "%~dp0"
python Diktafon.py
if errorlevel 1 (
    echo.
    echo === FEL UPPSTOD ===
    echo Kopiera texten ovan och skicka till utvecklaren.
    echo.
    pause
)
