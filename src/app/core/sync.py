"""
Synchronisation des stats vers le partage réseau.
Les données non transférées sont mises en file d'attente et envoyées au prochain démarrage.
"""
import json
import shutil
from pathlib import Path


def sync(user_id: str, stats: dict, network_path: str) -> bool:
    """
    Envoie les stats de l'utilisateur vers le partage réseau.
    Retourne True si réussi, False si réseau indisponible.
    """
    dest = Path(network_path) / "stats" / f"{user_id}.json"
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(stats, indent=2), encoding="utf-8")
        _clear_pending()
        return True
    except Exception:
        _save_pending(user_id, stats)
        return False


def sync_pending(network_path: str) -> None:
    pending = _load_pending()
    if not pending:
        return
    for user_id, stats in pending.items():
        if sync(user_id, stats, network_path):
            break  # _clear_pending() appelé dans sync()


def _pending_path() -> Path:
    from app.config import get_local_data_dir
    return get_local_data_dir() / "pending_sync.json"


def _load_pending() -> dict:
    path = _pending_path()
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_pending(user_id: str, stats: dict) -> None:
    pending = _load_pending()
    pending[user_id] = stats
    _pending_path().write_text(json.dumps(pending, indent=2), encoding="utf-8")


def _clear_pending() -> None:
    path = _pending_path()
    if path.exists():
        path.unlink()
