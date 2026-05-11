"""
Chargement de la liste des commandes Revit depuis data/revit_commands.json.
"""
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RevitCommand:
    code: str
    name: str
    category: str

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


def load() -> list[RevitCommand]:
    data_path = Path(__file__).parent.parent.parent.parent / "data" / "revit_commands.json"
    with open(data_path, encoding="utf-8") as f:
        return [RevitCommand(**item) for item in json.load(f)]


def search(commands: list[RevitCommand], query: str) -> list[RevitCommand]:
    q = query.lower().strip()
    if not q:
        return commands
    return [c for c in commands if q in c.code.lower() or q in c.name.lower() or q in c.category.lower()]
