# beepy

a small Discord bot that watches a channel and randomly chimes in using a local LLM.

beepy observes whatever's being said — by humans or other bots — and reacts with short, slightly unhinged responses. runs fully offline via [ollama](https://ollama.com).

## what it does

- connects to a Discord channel
- randomly decides whether to reply to each message (configurable chance)
- generates replies locally using ollama (default: `qwen2.5:0.5b`)
- keeps responses short and weird

## setup

**requirements**
- Python 3.10+
- [ollama](https://ollama.com) running locally with your chosen model pulled

```bash
ollama pull qwen2.5:0.5b
```

**install dependencies**
```bash
pip install -r requirements.txt
```

**configure**
```bash
cp config.example.json config.json
```

edit `config.json` with your values:
- `bot_token` — your Discord bot token
- `channel_id` — the channel to watch
- `a0at_bot_id` — the bot ID beepy watches
- `reply_chance` — probability of replying (0.0–1.0)
- `model` — ollama model to use

**run**
```bash
python watcher.py
```

## notes

- `config.json` is gitignored — never commit your bot token
- beepy never introduces itself, just reacts
- CPU-only, designed to run on a server
