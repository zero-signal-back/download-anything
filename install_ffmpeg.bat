@echo off
echo ========================================
echo FFmpeg Quick Installer
echo ========================================
echo.
echo Downloading FFmpeg...
powershell -Command "Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile 'ffmpeg.zip'"

echo.
echo Extracting...
powershell -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath '.' -Force"

echo.
echo Moving files...
for /d %%i in (ffmpeg-*) do (
    move "%%i\bin\ffmpeg.exe" "ffmpeg.exe"
    move "%%i\bin\ffprobe.exe" "ffprobe.exe"
)

echo.
echo Cleaning up...
del ffmpeg.zip
for /d %%i in (ffmpeg-*) do rd /s /q "%%i"

echo.
echo ========================================
echo FFmpeg installed successfully!
echo ========================================
echo.
echo Now restart your Flask app:
echo python app.py
echo.
pause
