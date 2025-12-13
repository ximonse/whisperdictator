@echo off
echo Installerar Whisper Diktafon beroenden...
echo.
echo Installerar FFmpeg via winget...
winget install Gyan.FFmpeg --silent --accept-package-agreements --accept-source-agreements
echo.
echo Installerar Python-paket...
pip install -r requirements.txt
echo.
echo ===========================================
echo Installation klar!
echo ===========================================
echo Dubbelklicka "Starta_Diktafon.bat" for att kora appen.
echo.
pause
