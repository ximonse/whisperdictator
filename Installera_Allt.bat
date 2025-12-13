@echo off
echo Installerar Whisper Diktafon beroenden...
echo.
echo Installerar OpenAI Whisper...
pip install openai-whisper
echo.
echo Installerar PyAudio (ljudinspelning)...
pip install pyaudio
echo.
echo Installerar pyperclip (urklipp)...
pip install pyperclip
echo.
echo Installerar pynput (global hotkey)...
pip install pynput
echo.
echo ===========================================
echo VIKTIGT: FFmpeg behövs för Whisper!
echo ===========================================
echo.
echo Installerar FFmpeg via Python...
pip install ffmpeg-python
echo.
echo ALTERNATIVT: Installera FFmpeg manuellt:
echo 1. Gå till https://www.gyan.dev/ffmpeg/builds/
echo 2. Ladda ner "release builds" zip
echo 3. Extrahera och lägg ffmpeg.exe i PATH
echo.
echo ===========================================
echo Installation klar!
echo ===========================================
echo Dubbelklicka "Starta_Diktafon.bat" for att kora appen.
echo.
pause