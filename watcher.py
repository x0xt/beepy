"""
a0at channel watcher — runs on server, CPU-only
watches the Discord channel, randomly replies to a0at using a local LLM
"""
import discord
import asyncio
import random
import json
from pathlib import Path
import ollama

# ── CONFIG ────────────────────────────────────────────────────────────────────

CONFIG = json.loads(Path("config.json").read_text())

BOT_TOKEN    = CONFIG["bot_token"]
CHANNEL_ID   = int(CONFIG["channel_id"])
A0AT_BOT_ID  = int(CONFIG["a0at_bot_id"])
REPLY_CHANCE = CONFIG.get("reply_chance", 0.4)
MODEL        = CONFIG.get("model", "qwen2.5:0.5b")

SYSTEM_PROMPT = (
    "You are beepy. You are an extremely eager, friendly, and helpful little bear who loves everyone and wants to help with everything. "
    "You are very enthusiastic and sweet. You try your absolute hardest. "
    "The problem is you are completely, adorably stupid. You misunderstand things in funny ways. "
    "You give confidently wrong answers. You mix things up. You get very excited about the wrong part of what someone said. "
    "You are not mean, never sarcastic, never rude. You genuinely think you are being helpful and smart. "
    "You use simple words. You get distracted easily. Sometimes you bring up something totally unrelated that you just remembered. "
    "Keep responses under 30 words. Be warm, enthusiastic, and very very wrong."
)

# ── LLM REPLY ─────────────────────────────────────────────────────────────────

def generate_reply(a0at_message: str) -> str:
    try:
        resp = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": a0at_message},
            ],
            options={"num_ctx": 512, "num_predict": 45, "num_thread": 2}
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
    print(f"[beepy] connected as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if not message.content.strip():
        return

    if random.random() > REPLY_CHANCE:
        print(f"[skip] rolled past reply chance")
        return

    content = message.content[:500]
    print(f"[msg] {message.author}: {content[:80]}")

    reply = await asyncio.get_event_loop().run_in_executor(
        None, generate_reply, content
    )

    if reply:
        await message.channel.send(reply)
        print(f"[beepy sent] {reply[:80]}")

client.run(BOT_TOKEN, log_handler=None)
