@echo off
cd /d "%~dp0"
echo Starting Otayori Post Server...
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Server stopped with error code %ERRORLEVEL%
    pause
)
