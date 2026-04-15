from datetime import datetime
from pathlib import Path

LOG_DIR  = Path("logs")
LOG_FILE = LOG_DIR / "chat.log"
LOG_DIR.mkdir(exist_ok=True)

def log_chat(author: str, user_msg: str, bot_reply: str):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {author}: {user_msg}\n")
        f.write(f"[{ts}] beepy: {bot_reply}\n\n")
