"""
Suivi d'utilisation mensuelle — enregistre les pressions XButton1/XButton2.
"""
import json
from datetime import datetime
from pathlib import Path


def get_stats_path() -> Path:
    from app.config import get_local_data_dir
    return get_local_data_dir() / "stats.json"


def record_press() -> None:
    path = get_stats_path()
    stats = _load(path)
    month = datetime.now().strftime("%Y-%m")
    stats[month] = stats.get(month, 0) + 1
    path.write_text(json.dumps(stats, indent=2), encoding="utf-8")


def get_monthly_count(month: str | None = None) -> int:
    month = month or datetime.now().strftime("%Y-%m")
    stats = _load(get_stats_path())
    return stats.get(month, 0)


def _load(path: Path) -> dict:
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}
