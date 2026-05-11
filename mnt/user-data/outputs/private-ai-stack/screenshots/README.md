# Screenshots

This folder holds the screenshots referenced in the main README. The
README currently uses [placehold.co](https://placehold.co) URLs as
placeholders so the page renders cleanly on GitHub. Once you have real
screenshots, drop them here with the filenames below and update the
image references in `README.md` to point at the local files.

## What to capture

### `01-openwebui-chat.png` — hero image at the top of the README
The main chat interface, mid-conversation. Show the model dropdown
clearly so people can see this is a real local model. Ideally include
some code or formatted output so the response styling is visible.

**Suggested size:** 1200 × 600 (or wider — GitHub will scale down).

### `02-openwebui-connections.png` — Open WebUI Step 6
The Admin Panel → Settings → Connections page, showing the `ollama-auth`
entry with the API key field visible (but obscured — black bar over the
actual key value).

**Suggested size:** 1000 × 500.

### `03-telegram-bot.png` — bot section
A real Telegram conversation with your bot. Include `/start`, a real
question, and a real response so people can see what the experience
looks like. Optionally show the bot's terminal output in a second
screenshot.

**Suggested size:** 900 × 600 (or vertical 600 × 1000 for a phone
screenshot — both work).

### `04-continue-vscode.png` — Continue section
The Continue chat panel open in VS Code with a code-related question
and a streaming response. If you can capture tab autocomplete (the
ghost text) in a separate shot, even better.

**Suggested size:** 1200 × 700.

## Optional extras you might add

- `05-bot-rejection.png` — bot terminal showing a `[REJECTED]` line when
  an unauthorized user tries to message it. Good for the security
  section.
- `06-phone-access.png` — Open WebUI running on your phone over the LAN.
  Adds visual proof for the "accessible from anywhere on your network"
  claim.
- `07-mermaid-rendered.png` — only if Mermaid rendering breaks for some
  readers (it shouldn't on GitHub.com, but the placeholder is here just
  in case).

## How to update the README to use real screenshots

Find each `placehold.co` image URL in `README.md` and replace it with a
relative path to the local file:

```diff
- ![alt text](https://placehold.co/1200x600/0f172a/94a3b8?text=...)
+ ![alt text](screenshots/01-openwebui-chat.png)
```

That's it. No other changes needed.

## Tips

- **PNG over JPG** for anything with text — JPG artifacts make UI text
  blurry and unreadable.
- **Crop tight** before exporting. Don't include your taskbar or other
  windows unless they add context.
- **Redact carefully.** Black out usernames, real API keys (even partial
  ones), Telegram user IDs, real IP addresses, and anything in your
  browser tabs you wouldn't want public. A `repr()` of an env var is
  surprisingly easy to leak in a terminal screenshot.
- **Consistent style.** If you use one OS theme, stick with it across
  all screenshots. Dark mode reads better on GitHub for most people.
