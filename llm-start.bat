@echo off
REM ============================================================
REM llm-start.bat — bring the LLM stack online
REM ============================================================
REM Use this when you're done gaming and want your local AI back.
REM
REM Starts Ollama (loads models into VRAM on first request),
REM ensures the Caddy auth proxy is running, and launches the
REM Telegram bot in a separate window for visibility.
REM ============================================================

echo Starting Ollama...
start "" "%LOCALAPPDATA%\Programs\Ollama\ollama.exe"

REM Wait a few seconds for Ollama to come online before things that depend on it
timeout /t 3 /nobreak >nul

echo Ensuring Caddy auth proxy is running...
docker start ollama-auth >nul 2>&1

echo Starting Telegram bot in a separate window...
REM Adjust the path below to wherever bot.py lives
start "Telegram Bot" cmd /k "cd /d D:\TelegramBot && python bot.py"

echo.
echo All systems started:
echo   - Ollama on 127.0.0.1:11500
echo   - Caddy auth proxy on 127.0.0.1:11434
echo   - Open WebUI at https://localhost
echo   - Telegram bot in separate window
echo.
echo Models will load on first use (~30-90 seconds depending on storage).
pause
