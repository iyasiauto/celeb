@echo off
cd /d "%~dp0"
python make_video.py %*
pause
