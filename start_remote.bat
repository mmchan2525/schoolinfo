@echo off
chcp 65001 > nul
echo ========================================================
echo   おたよりポスト (Otayori Post) - 外出先アクセス起動中
echo ========================================================
echo.

start "Otayori Server" cmd /k "python main.py"
timeout /t 2 > nul
start "Cloudflare Tunnel" cmd /k "cloudflared.exe tunnel --url http://127.0.0.1:8000"

echo.
echo サーバーと外出先用HTTPSトンネルを起動しました！
echo ウィンドウに表示される「https://xxxx.trycloudflare.com」にスマホからアクセスしてください。
echo.
pause
