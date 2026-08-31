@echo off
title YouTube Long-Form 30+ Min Documentary Production Pipeline
echo ============================================================
echo YOUTUBE LONG-FORM 30+ MIN DOCUMENTARY PRODUCTION PIPELINE
echo 100% GPU NVENC Acceleration on NVIDIA GeForce RTX
echo ============================================================
echo.

set /p TITLE="Enter Documentary Title: "
set /p SCRIPT="Enter Path to Script TXT File: "
set /p OUTDIR="Enter Output Directory: "

if "%OUTDIR%"=="" set OUTDIR=C:\Users\%USERNAME%\Downloads

echo.
echo Starting Production Pipeline...
python pipeline.py --title "%TITLE%" --script "%SCRIPT%" --output-dir "%OUTDIR%"

echo.
echo ============================================================
echo Pipeline Execution Finished! Check output directory.
echo ============================================================
pause
