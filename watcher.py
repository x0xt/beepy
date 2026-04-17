"""
beepy — entry point. discord client and event handlers only.
"""
import re
import random
import discord

from config import BOT_TOKEN, PRIVACY_REPLY
from llm import generate_reply
from logger import log_chat
from chance import current_reply_chance, starting_chance

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"[beepy] connected as {client.user} | reply chance: {starting_chance():.0%}")

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

    async with message.channel.typing():
        reply = await generate_reply(content)

    if reply:
        # split by paragraph then chunk anything over 1990 chars
        raw_paragraphs = [p.strip() for p in reply.split('\n\n') if p.strip()]
        chunks = []
        for p in raw_paragraphs:
            while len(p) > 1990:
                chunks.append(p[:1990])
                p = p[1990:]
            if p:
                chunks.append(p)

        use_reply = replied_to_beepy or (not targeted and random.random() < 0.5)
        for i, chunk in enumerate(chunks):
            if use_reply and i == 0:
                await message.reply(chunk, mention_author=False)
            else:
                await message.channel.send(chunk)
            if len(chunks) > 1:
                await asyncio.sleep(0.8)
        log_chat(author, content, reply)
        print(f"[beepy] {reply[:80]}")

client.run(BOT_TOKEN, log_handler=None)
