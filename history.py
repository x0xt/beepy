"""
Per-channel conversation history for beepy.
Keeps the full thread in memory with a TTL.
"""

import time

TTL_SECONDS = 3600  # 1 hour of inactivity clears the history
MAX_MESSAGES = 200  # cap to avoid runaway memory

_store = {}  # channel_id -> {"messages": [...], "last_at": float}


def get_history(channel_id: str) -> list:
    entry = _store.get(channel_id)
    if not entry:
        return []
    if time.time() - entry["last_at"] > TTL_SECONDS:
        del _store[channel_id]
        return []
    return entry["messages"]


def push_history(channel_id: str, role: str, content: str):
    if channel_id not in _store:
        _store[channel_id] = {"messages": [], "last_at": time.time()}
    entry = _store[channel_id]
    entry["messages"].append({"role": role, "content": content})
    if len(entry["messages"]) > MAX_MESSAGES:
        entry["messages"] = entry["messages"][-MAX_MESSAGES:]
    entry["last_at"] = time.time()


def clear_history(channel_id: str):
    _store.pop(channel_id, None)
