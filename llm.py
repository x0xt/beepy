import random
import ollama
from config import MODEL, SYSTEM_PROMPT, HARD_STOP_FALLBACKS
from guardrail import with_retry, is_refusal

_client = ollama.Client(host="http://127.0.0.1:11435", timeout=60)

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

def _call_model(content: str) -> str | None:
    try:
        tokens = random.randint(20, 100)
        resp = _client.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": content},
            ],
            options={"num_ctx": 512, "num_predict": tokens, "num_thread": 2},
            keep_alive=-1,
        )
        return resp["message"]["content"].strip()
    except Exception as e:
        print(f"[llm error] {e}")
        return None

def generate_reply(content: str) -> str | None:
    raw = with_retry(_call_model, content, fallbacks=HARD_STOP_FALLBACKS)
    return mangle_text(raw) if raw else raw
