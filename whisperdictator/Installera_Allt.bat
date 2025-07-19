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
echo Installation klar!
echo ===========================================
echo Dubbelklicka "Starta_Diktafon.bat" for att kora appen.
echo.
pause