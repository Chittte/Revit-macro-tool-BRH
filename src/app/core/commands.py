"""
Chargement de la liste des commandes Revit depuis data/revit_commands.json.
"""
import json
from dataclasses import dataclass
from pathlib import Path

from app.core import logger


@dataclass
class RevitCommand:
    code: str
    name: str
    category: str

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


def load() -> list[RevitCommand]:
    data_path = Path(__file__).parent.parent.parent.parent / "data" / "revit_commands.json"
    try:
        with open(data_path, encoding="utf-8") as f:
            commands = [RevitCommand(**item) for item in json.load(f)]
        logger.success(f"Commandes Revit chargées : {len(commands)} entrées")
        return commands
    except FileNotFoundError:
        logger.error(f"Fichier introuvable : {data_path}")
        return []
    except Exception as e:
        logger.error("Erreur chargement commandes Revit", e)
        return []


def search(commands: list[RevitCommand], query: str) -> list[RevitCommand]:
    q = query.lower().strip()
    if not q:
        return commands
    return [c for c in commands if q in c.code.lower() or q in c.name.lower() or q in c.category.lower()]
