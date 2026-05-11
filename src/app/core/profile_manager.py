"""
Gestion des profils — chaque profil a ses propres assignations de touches.
Persistance dans data_local/profiles.json.
"""
from __future__ import annotations
import configparser
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


def import_from_ini(ini_path: Path) -> list[dict]:
    """Importe les profils depuis un MacroProfils.ini v1 (UTF-16)."""
    try:
        raw = ini_path.read_bytes()
        text = raw.decode("utf-16")
    except Exception as e:
        logger.error("Impossible de lire le fichier INI", e)
        return []

    config = configparser.ConfigParser()
    try:
        config.read_string(text)
    except Exception as e:
        logger.error("Erreur de lecture INI", e)
        return []

    try:
        count = int(config.get("Profiles", "Count", fallback="0"))
    except Exception:
        count = 0

    profiles = []
    for i in range(1, count + 1):
        section = f"Profile_{i}"
        if not config.has_section(section):
            continue

        name  = config.get(section, "Name",  fallback=f"Profil {i}").strip()
        ptype = config.get(section, "Type",  fallback="key").strip()
        key1  = config.get(section, "Key1",  fallback="").strip()
        key2  = config.get(section, "Key2",  fallback="").strip()
        text1 = config.get(section, "Text1", fallback="").strip()
        text2 = config.get(section, "Text2", fallback="").strip()

        assignments: dict = {}

        if ptype == "key":
            if key1:
                assignments["XButton1"] = [{"type": "key", "value": key1.upper()}]
            if key2:
                assignments["XButton2"] = [{"type": "key", "value": key2.upper()}]
        else:
            if text1:
                assignments["XButton1"] = [{"type": "text", "value": text1}]
            if text2:
                assignments["XButton2"] = [{"type": "text", "value": text2}]

        p = new_profile(name)
        p["assignments"] = assignments
        profiles.append(p)
        logger.info(f"Importé : {name} ({ptype})")

    return profiles


def _default_profiles() -> list[dict]:
    return [new_profile("Général")]
