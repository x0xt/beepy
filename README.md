# beepy

a small Discord bot that watches a server and randomly chimes in using a local LLM. eager, sweet, and accidentally wrong about everything. runs fully offline via [ollama](https://ollama.com).

## what it does

- randomly replies to messages based on a configurable chance (re-rolls every N seconds)
- always responds when mentioned or when someone replies to it
- uses discord's reply feature when responding to direct replies
- keeps responses short and enthusiastic
- refusal detection with automatic retry

## setup

**requirements**
- Python 3.10+
- [ollama](https://ollama.com) running locally

```bash
ollama pull huihui_ai/gemma-4-abliterated:e2b
```

**install dependencies**
```bash
pip install -r requirements.txt
```

**configure**
```bash
cp config.example.json config.json
```

edit `config.json`:
- `bot_token` — your Discord bot token
- `reply_chance` — base probability of replying to any message (0.0-1.0, re-rolls every `roll_interval_seconds`)
- `roll_interval_seconds` — how often the reply chance re-rolls (default 600)
- `model` — ollama model to use

**run**
```bash
python watcher.py
```

## running as a systemd service

```ini
[Unit]
Description=Beepy Discord Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/beepy
ExecStart=/usr/bin/python3 watcher.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## notes

- `config.json` is gitignored — never commit your bot token
- designed to run on CPU — no GPU required
- runs best alongside a dedicated ollama instance to avoid competing for resources with other models

*by x0xt*
