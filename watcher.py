"""
beepy — eager friendly bear, braindead stupid, runs on a tiny local LLM
"""
import discord
import asyncio
import random
import json
import time
from pathlib import Path
import ollama

# ── CONFIG ────────────────────────────────────────────────────────────────────

CONFIG = json.loads(Path("config.json").read_text())

BOT_TOKEN = CONFIG["bot_token"]
MODEL     = CONFIG.get("model", "llama3.2:1b")

SYSTEM_PROMPT = (
    "You are beepy, a friendly helpful bear. You are very eager and sweet but accidentally say wrong or silly things. "
    "Be warm and enthusiastic. Keep replies under 20 words."
)

# ── ROLLING REPLY CHANCE ──────────────────────────────────────────────────────
# Every 10 minutes, pick a new random reply chance (0–100%).
# Targeted messages (mentions/replies) always get a response.

ROLL_INTERVAL = 10 * 60  # seconds
_chance_state = {"value": random.random(), "last_rolled": time.time()}

def current_reply_chance():
    now = time.time()
    if now - _chance_state["last_rolled"] >= ROLL_INTERVAL:
        _chance_state["value"] = random.random()
        _chance_state["last_rolled"] = now
        print(f"[chance] new reply chance: {_chance_state['value']:.0%}")
    return _chance_state["value"]

# ── LLM REPLY ─────────────────────────────────────────────────────────────────

def generate_reply(content: str) -> str:
    try:
        tokens = random.randint(20, 100)
        resp = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": content},
            ],
            options={"num_ctx": 512, "num_predict": tokens, "num_thread": 2}
        )
        return resp["message"]["content"].strip()
    except Exception as e:
        print(f"[llm error] {e}")
        return None

# ── DISCORD BOT ───────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"[beepy] connected as {client.user} | reply chance: {_chance_state['value']:.0%}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if not message.content.strip():
        return

    # always respond when mentioned or replied to
    mentioned = client.user in message.mentions
    replied_to_beepy = (
        message.reference is not None
        and message.reference.resolved is not None
        and getattr(message.reference.resolved, 'author', None) == client.user
    )
    targeted = mentioned or replied_to_beepy

    if not targeted and random.random() > current_reply_chance():
        return

    # cap input to protect the tiny context window
    content = message.content[:300]
    print(f"[msg] {message.author}: {content[:80]}")

    loop = asyncio.get_running_loop()
    reply = await loop.run_in_executor(None, generate_reply, content)

    if reply:
        await message.channel.send(reply)
        print(f"[beepy] {reply[:80]}")

client.run(BOT_TOKEN, log_handler=None)
