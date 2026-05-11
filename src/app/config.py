"""
Gestion de la configuration locale (config.json).
"""
import json
import uuid
from pathlib import Path


_CONFIG_PATH = Path(__file__).parent.parent.parent / "config.json"
_LOCAL_DATA_DIR = Path(__file__).parent.parent.parent / "data_local"


def load() -> dict:
    if _CONFIG_PATH.exists():
        with open(_CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save(config: dict) -> None:
    _CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")


def get_or_create_user_id() -> str:
    config = load()
    if "user_id" not in config:
        config["user_id"] = str(uuid.uuid4())
        save(config)
    return config["user_id"]


def get_network_path() -> str:
    return load().get("network_path", "")


def get_local_data_dir() -> Path:
    _LOCAL_DATA_DIR.mkdir(exist_ok=True)
    return _LOCAL_DATA_DIR
