import random
import ollama
from config import MODEL, SYSTEM_PROMPT, HARD_STOP_FALLBACKS

def mangle_word(word: str) -> str:
    if len(word) < 3:
        return word
    kind = random.random()
    i = random.randint(0, len(word) - 2)
    if kind < 0.33:
        lst = list(word)
        lst[i], lst[i+1] = lst[i+1], lst[i]
        return ''.join(lst)
    elif kind < 0.66:
        return word[:i] + word[i] + word[i:]
    else:
        return word[:i] + word[i+1:]

def mangle_text(text: str, chance: float = 0.01) -> str:
    words = text.split(' ')
    return ' '.join(mangle_word(w) if random.random() < chance else w for w in words)

def strip_hard_stops(text: str) -> str:
    if text.lower().strip().startswith(("i cannot", "i can't", "i'm unable", "i am unable", "i won't")):
        return random.choice(HARD_STOP_FALLBACKS)
    return text

def generate_reply(content: str) -> str | None:
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
