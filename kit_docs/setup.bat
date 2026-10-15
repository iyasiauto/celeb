@echo off
cd /d "%~dp0"
echo Installing Docu Templates (Python packages, Chromium, FFmpeg)...
python --version || (echo Python not found. Install Python 3.10+ from python.org and tick "Add python.exe to PATH". & pause & exit /b 1)
python -m pip install --upgrade pip
python -m pip install -r docu\requirements.txt static-ffmpeg anthropic
python -m playwright install chromium
python -c "import static_ffmpeg; static_ffmpeg.add_paths(); import shutil; print('ffmpeg:', shutil.which('ffmpeg'))"
if not exist api_keys\keys.env copy api_keys\keys.example.env api_keys\keys.env >nul
echo.
echo Done. Put your keys (optional) in api_keys\keys.env, then double-click run.bat
pause
