"""
Local LLM Telegram Bot
======================

A single-file Telegram bot that proxies messages to a local Ollama
instance through a Caddy auth gateway. Includes a per-user-ID whitelist,
conversation memory per user, and graceful error handling.

Setup:
    pip install -r requirements.txt

Required environment variables (set via System Properties on Windows or
your shell's .rc on Linux/macOS):

    TELEGRAM_BOT_TOKEN       - get from @BotFather on Telegram
    OLLAMA_API_KEY           - bearer token (no "Bearer " prefix)
    TELEGRAM_ALLOWED_USERS   - comma-separated Telegram user IDs

Run:
    python bot.py
"""

import os
import httpx
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ============================================================
# CONFIG — secrets loaded from environment variables
# ============================================================
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY")
ALLOWED_USERS_RAW = os.environ.get("TELEGRAM_ALLOWED_USERS", "")

# Fail loudly at startup if any required secret is missing — better than
# discovering it 3 hours later via a confusing 401 in the logs
if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN env var is not set")
if not OLLAMA_API_KEY:
    raise RuntimeError("OLLAMA_API_KEY env var is not set")
if not ALLOWED_USERS_RAW:
    raise RuntimeError(
        "TELEGRAM_ALLOWED_USERS env var is not set (comma-separated IDs)"
    )

# Parse comma-separated user IDs into a set of ints for fast membership checks
ALLOWED_USERS = {
    int(uid.strip()) for uid in ALLOWED_USERS_RAW.split(",") if uid.strip()
}

# Hits Caddy (auth proxy on :11434), which forwards to Ollama on :11500
OLLAMA_URL = "http://localhost:11434/api/chat"

# Pick a model that's fast enough for chat. 14B-class models give a good
# response time on a 16GB GPU. Larger MoE models like 30B-A3B also work
# but feel sluggish in a chat context.
MODEL = "qwen3:14b"
# ============================================================

# System prompt — defines how the AI behaves
SYSTEM_PROMPT = (
    "You are an expert AI assistant. You are helpful, thorough, and give "
    "detailed accurate answers. When writing code always include comments "
    "and explain your reasoning."
)

# In-process conversation memory — wiped on bot restart.
# For persistence across restarts, swap this for SQLite (~20 lines of code).
conversation_history: dict[int, list[dict]] = {}


def is_authorized(update: Update) -> bool:
    """Whitelist check — only allow specific Telegram user IDs through."""
    user = update.effective_user
    if user is None:
        return False
    return user.id in ALLOWED_USERS


async def reject(update: Update) -> None:
    """Polite rejection for non-allowlisted users; logs who tried.

    Logging the attempt is useful for noticing if someone discovers your
    bot username and starts probing.
    """
    user = update.effective_user
    print(
        f"[REJECTED] Unauthorized access attempt: "
        f"user_id={user.id} username=@{user.username}"
    )
    await update.message.reply_text("Sorry, this bot is private.")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /start — clears history and sends welcome message."""
    if not is_authorized(update):
        return await reject(update)
    user_id = update.message.from_user.id
    conversation_history[user_id] = []
    await update.message.reply_text(
        "Hey! I'm your local AI assistant. Ask me anything!"
    )


async def handle_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Main handler — sends user message + history to Ollama via Caddy."""
    if not is_authorized(update):
        return await reject(update)

    user_message = update.message.text
    user_id = update.message.from_user.id

    if user_id not in conversation_history:
        conversation_history[user_id] = []

    # Add the user's new message to their history
    conversation_history[user_id].append(
        {"role": "user", "content": user_message}
    )

    # Keep last 10 exchanges (20 messages) to bound the prompt size and
    # avoid hitting context limits on long conversations
    if len(conversation_history[user_id]) > 20:
        conversation_history[user_id] = conversation_history[user_id][-20:]

    await update.message.reply_text("Thinking...")

    try:
        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.post(
                OLLAMA_URL,
                # Bearer auth → Caddy validates → strips header → forwards to Ollama.
                # The OLLAMA_API_KEY env var should be JUST the key, no "Bearer "
                # prefix — the f-string below adds that.
                headers={"Authorization": f"Bearer {OLLAMA_API_KEY}"},
                json={
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        *conversation_history[user_id],
                    ],
                    # Non-streaming for simplicity. Streaming would let
                    # users see the response as it generates, but adds
                    # complexity around message editing.
                    "stream": False,
                },
            )
            # Raise for 4xx/5xx so we don't silently swallow auth failures
            response.raise_for_status()
            data = response.json()
            reply = data["message"]["content"]

            # Save the assistant's reply to history so context carries forward
            conversation_history[user_id].append(
                {"role": "assistant", "content": reply}
            )

            # Telegram caps messages at 4096 characters — chunk if needed
            if len(reply) > 4096:
                for i in range(0, len(reply), 4096):
                    await update.message.reply_text(reply[i : i + 4096])
            else:
                await update.message.reply_text(reply)

    except httpx.HTTPStatusError as e:
        # Surfaces the real cause when Caddy 401s (key mismatch) or
        # Ollama returns an error mid-generation
        body_preview = e.response.text[:200] if e.response.text else "(empty body)"
        await update.message.reply_text(
            f"Ollama returned HTTP {e.response.status_code}"
        )
        print(f"[HTTP ERROR] {e.response.status_code} — {body_preview}")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
        print(f"[ERROR] {e!r}")


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for /clear — wipes this user's conversation history."""
    if not is_authorized(update):
        return await reject(update)
    user_id = update.message.from_user.id
    conversation_history[user_id] = []
    await update.message.reply_text("Memory cleared! Starting fresh.")


if __name__ == "__main__":
    print(f"Authorized users: {ALLOWED_USERS}")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    print("Bot is running...")
    app.run_polling()
