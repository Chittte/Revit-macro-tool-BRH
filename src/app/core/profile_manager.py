"""
Gestion des profils — chaque profil a ses propres assignations de touches.
Persistance dans data_local/profiles.json.
"""
from __future__ import annotations
import json
import uuid
from pathlib import Path

from app.core import logger

SequenceItem = dict  # {"type": "key"|"text", "value": str}

PROFILES_PATH = Path(__file__).parent.parent.parent.parent / "data_local" / "profiles.json"


def load() -> list[dict]:
    if not PROFILES_PATH.exists():
        default = _default_profiles()
        save(default)
        return default
    try:
        with open(PROFILES_PATH, encoding="utf-8") as f:
            data = json.load(f)
        logger.success(f"Profils chargés : {len(data)} profils")
        return data
    except Exception as e:
        logger.error("Échec chargement des profils", e)
        return _default_profiles()


def save(profiles: list[dict]) -> None:
    PROFILES_PATH.parent.mkdir(exist_ok=True)
    PROFILES_PATH.write_text(json.dumps(profiles, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"Profils sauvegardés : {len(profiles)} profils")


def new_profile(name: str) -> dict:
    return {"id": str(uuid.uuid4())[:8], "name": name, "assignments": {}}


def _default_profiles() -> list[dict]:
    return [new_profile("Général")]
