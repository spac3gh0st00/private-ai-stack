@echo off
REM ============================================================
REM llm-stop.bat — tear down the LLM stack to free GPU/VRAM
REM ============================================================
REM Use this before launching a GPU-heavy game so Ollama isn't
REM hogging VRAM or CPU.
REM
REM Stops the bot's window first, then unloads models from VRAM,
REM then kills Ollama itself. Docker containers stay up — they
REM use trivial CPU/RAM and zero GPU when idle.
REM ============================================================

echo Stopping Telegram bot...
REM Closes only the bot's window — identified by its title
taskkill /FI "WINDOWTITLE eq Telegram Bot" /F >nul 2>&1

echo Stopping Ollama models...
REM Unload each loaded model from VRAM. Adjust this list to match
REM whatever models you actually use.
ollama stop qwen3.6:35b-a3b >nul 2>&1
ollama stop qwen3:14b >nul 2>&1
ollama stop deepseek-r1:14b >nul 2>&1

echo Killing Ollama process...
taskkill /IM ollama.exe /F >nul 2>&1

echo.
echo Done! VRAM is free for gaming.
pause
