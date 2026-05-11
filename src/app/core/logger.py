"""
Système de log central — diffuse en temps réel à l'UI et écrit dans un fichier.
"""
from __future__ import annotations
import threading
from datetime import datetime
from pathlib import Path
from typing import Callable


LOG_FILE = Path(__file__).parent.parent.parent.parent / "logs" / "app.log"

_lock = threading.Lock()
_entries: list[dict] = []
_callbacks: list[Callable[[dict], None]] = []


def info(msg: str) -> None:
    _log("INFO", msg)


def success(msg: str) -> None:
    _log("SUCCESS", msg)


def warning(msg: str) -> None:
    _log("WARNING", msg)


def error(msg: str, exc: Exception | None = None) -> None:
    full_msg = f"{msg} — {exc}" if exc else msg
    _log("ERROR", full_msg)


def subscribe(callback: Callable[[dict], None]) -> None:
    with _lock:
        _callbacks.append(callback)


def unsubscribe(callback: Callable[[dict], None]) -> None:
    with _lock:
        _callbacks.remove(callback)


def get_all() -> list[dict]:
    with _lock:
        return list(_entries)


def _log(level: str, msg: str) -> None:
    entry = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "level": level,
        "msg": msg,
    }
    with _lock:
        _entries.append(entry)
        callbacks = list(_callbacks)
    _write_to_file(entry)
    for cb in callbacks:
        try:
            cb(entry)
        except Exception:
            pass


def _write_to_file(entry: dict) -> None:
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{entry['time']}] [{entry['level']:7}] {entry['msg']}\n")
    except Exception:
        pass
