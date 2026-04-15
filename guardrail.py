"""
guardrail.py — detects and retries LLM hard stops / refusals.

Drop-in for any ollama project:
  from guardrail import is_refusal, with_retry

is_refusal(text)            → bool
with_retry(fn, *args)       → calls fn(*args) up to MAX_RETRIES times,
                              returning the first non-refusal response.
                              Falls back to a random FALLBACK if all attempts refuse.
"""

import random

MAX_RETRIES = 3

FALLBACKS = [
    "oh!! um... i got a little confused!! hehe!!",
    "wait what happened?? i think i missed something!!",
    "oh no!! i blanked!! what were we talking about?!",
    "um!! okay!! i'm not sure what to say but i'm still here!!",
    "hehe... sorry!! my brain went fuzzy for a second!!",
]

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

def with_retry(fn, *args, fallbacks: list[str] = None, max_retries: int = MAX_RETRIES) -> str:
    """
    Call fn(*args) up to max_retries times.
    Returns first response that isn't a refusal.
    Falls back to a random entry from fallbacks (or built-in FALLBACKS) if all fail.
    """
    fb = fallbacks if fallbacks is not None else FALLBACKS
    for attempt in range(max_retries):
        result = fn(*args)
        if result and not is_refusal(result):
            return result
        print(f"[guardrail] refusal detected (attempt {attempt + 1}/{max_retries}), retrying...")
    print(f"[guardrail] all {max_retries} attempts refused, using fallback")
    return random.choice(fb)
