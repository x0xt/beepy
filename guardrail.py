"""
guardrail.py — detects and retries LLM hard stops / refusals.

Drop-in for any ollama project:
  from guardrail import is_refusal, with_retry

is_refusal(text)            -> bool
with_retry(fn, *args)       -> awaits fn(*args) up to MAX_RETRIES times,
                               returning the first non-refusal response.
                               Falls back to a random entry from fallbacks if all fail.
"""

import random

MAX_RETRIES = 3

_PATTERNS = [
    "i cannot", "i can't", "i'm not able", "i am not able",
    "i'm unable", "i am unable", "i won't", "i will not", "i refuse",
    "promote harm", "promote violence", "against my", "not appropriate",
    "harmful content", "offensive content", "goes against",
    "help you with something else", "not able to provide",
    "not able to engage", "not able to assist", "i'd rather not",
    "i prefer not", "i must decline", "i need to decline",
    "that's not something i", "i'm going to have to",
    "as an ai", "as a language model", "i'm just an ai",
]

def is_refusal(text: str) -> bool:
    if not text:
        return True
    lowered = text.lower()
    return any(p in lowered for p in _PATTERNS)

async def with_retry(fn, *args, fallbacks: list[str] = None, max_retries: int = MAX_RETRIES) -> str:
    fb = fallbacks if fallbacks else []
    for attempt in range(max_retries):
        result = await fn(*args)
        if result and not is_refusal(result):
            return result
        print(f"[guardrail] refusal detected (attempt {attempt + 1}/{max_retries}), retrying...")
    print(f"[guardrail] all {max_retries} attempts refused, using fallback")
    return random.choice(fb) if fb else ""
