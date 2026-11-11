# discord-gpt-bot

A simple Discord bot that answers with ChatGPT when you @mention it or DM it.
It remembers the last few messages in each channel, so follow-ups work.

Also comes with a tiny web panel (`app.py`) for testing prompts in the browser.

## Features

- Replies when mentioned or in DMs
- Short per-channel memory (`!reset` to clear it)
- Long answers split automatically (Discord's 2000 char limit)
- Works with any OpenAI-compatible API (set `OPENAI_BASE_URL`)
- `/health` endpoint for UptimeRobot

## Setup

1. Make a bot at https://discord.com/developers/applications and turn on **Message Content Intent**.
2. Install the requirements:

   ```
   pip install -r requirements.txt
   ```

3. Fill in your keys in `.env` (see below).
4. Run it:

   ```
   python bot.py
   ```

   And for the web panel:

   ```
   python app.py
   ```

## .env

```
DISCORD_TOKEN=
OPENAI_API_KEY=
OPENAI_BASE_URL=
OPENAI_MODEL=gpt-4o-mini
```

## Notes

- Hosted on my VPS with pm2, restarts on crash.
- TODO: slash commands, per-server settings, rate limit per user.
