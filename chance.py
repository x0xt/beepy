import random
import time
from config import ROLL_INTERVAL, REPLY_CHANCE

_state = {"value": REPLY_CHANCE, "last_rolled": time.time()}

def current_reply_chance() -> float:
    now = time.time()
    if now - _state["last_rolled"] >= ROLL_INTERVAL:
        _state["value"] = random.random()
        _state["last_rolled"] = now
        print(f"[chance] new reply chance: {_state['value']:.0%}")
    return _state["value"]

def starting_chance() -> float:
    return _state["value"]
