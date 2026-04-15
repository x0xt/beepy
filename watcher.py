"""
beepy — eager, sweet, accidentally stupid. runs on a tiny local LLM.
"""
import discord
import asyncio
import random
import json
import re
import time
from datetime import datetime
from pathlib import Path
import ollama

# ── CONFIG ────────────────────────────────────────────────────────────────────

CONFIG = json.loads(Path("config.json").read_text())

BOT_TOKEN = CONFIG["bot_token"]
MODEL     = CONFIG.get("model", "llama3.2:1b")

SYSTEM_PROMPT = (
    "You are beepy. You are very eager, sweet, and want to help everyone. "
    "You try your best but accidentally say wrong or silly things. "
    "Be warm and enthusiastic. Keep replies short."
)

PRIVACY_REPLY = (
    "oh!! yes!! beepy keeps a little log of conversations to get better at helping!! "
    "i hope that's okay!! i think it's okay!! it's probably okay!!"
)

HARD_STOP_FALLBACKS = [
    "oh!! um... i got a little confused!! hehe!!",
    "wait what happened?? i think i missed something!!",
    "oh no!! i blanked!! what were we talking about?!",
    "um!! okay!! i'm not sure what to say but i'm still here!!",
    "hehe... sorry!! my brain went fuzzy for a second!!",
]

def mangle_word(word: str) -> str:
    if len(word) < 3:
        return word
    kind = random.random()
    i = random.randint(0, len(word) - 2)
    if kind < 0.33:
        # swap two adjacent letters
        lst = list(word)
        lst[i], lst[i+1] = lst[i+1], lst[i]
        return ''.join(lst)
    elif kind < 0.66:
        # double a random letter
        return word[:i] + word[i] + word[i:]
    else:
        # drop a random letter
        return word[:i] + word[i+1:]

def mangle_text(text: str, chance: float = 0.01) -> str:
    words = text.split(' ')
    return ' '.join(mangle_word(w) if random.random() < chance else w for w in words)

def strip_hard_stops(text: str) -> str | None:
    lowered = text.lower().strip()
    if lowered.startswith(("i cannot", "i can't", "i'm unable", "i am unable", "i won't")):
        return random.choice(HARD_STOP_FALLBACKS)
    return text

# ── LOGGING ───────────────────────────────────────────────────────────────────

LOG_DIR  = Path("logs")
LOG_FILE = LOG_DIR / "chat.log"
LOG_DIR.mkdir(exist_ok=True)

def log_chat(author: str, user_msg: str, bot_reply: str):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {author}: {user_msg}\n")
        f.write(f"[{ts}] beepy: {bot_reply}\n\n")

# ── ROLLING REPLY CHANCE ──────────────────────────────────────────────────────
# Every 10 minutes, pick a new random reply chance (0–100%).
# Targeted messages (mentions/replies) always get a response.

ROLL_INTERVAL = 10 * 60
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
        raw = strip_hard_stops(resp["message"]["content"].strip())
        return mangle_text(raw) if raw else raw
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

    mentioned = client.user in message.mentions
    replied_to_beepy = (
        message.reference is not None
        and message.reference.resolved is not None
        and getattr(message.reference.resolved, 'author', None) == client.user
    )
    targeted = mentioned or replied_to_beepy

    if not targeted and random.random() > current_reply_chance():
        return

    # strip mentions and extra whitespace before sending to model
    content = re.sub(r'<@!?\d+>', '', message.content).strip()[:300]
    author  = str(message.author)
    print(f"[msg] {author}: {content[:80]}")

    # privacy policy trigger
    if "privacy policy" in content.lower():
        await message.channel.send(PRIVACY_REPLY)
        log_chat(author, content, PRIVACY_REPLY)
        return

    loop = asyncio.get_running_loop()
    async with message.channel.typing():
        reply = await loop.run_in_executor(None, generate_reply, content)

    if reply:
        paragraphs = [p.strip() for p in reply.split('\n\n') if p.strip()]
        for p in paragraphs:
            await message.channel.send(p)
            if len(paragraphs) > 1:
                await asyncio.sleep(0.8)
        log_chat(author, content, reply)
        print(f"[beepy] {reply[:80]}")

client.run(BOT_TOKEN, log_handler=None)
