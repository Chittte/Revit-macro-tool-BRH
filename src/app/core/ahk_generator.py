"""
Génère le script AHK à partir de la configuration d'assignation clavier/souris.
"""
from pathlib import Path


AHK_HEADER = """\
#Requires AutoHotkey v1.1
#SingleInstance Force
#NoEnv
SetWorkingDir %A_ScriptDir%

; Revit Macro Tool — script généré automatiquement
; Ne pas modifier manuellement.

"""


def generate(assignments: dict[str, str], output_path: Path) -> None:
    """
    assignments : {"XButton1": "VV", "XButton2": "CP", "F1": "DI", ...}
    output_path : chemin du fichier .ahk à écrire
    """
    lines = [AHK_HEADER]
    for key, command in assignments.items():
        ahk_key = _to_ahk_key(key)
        lines.append(f"{ahk_key}::\n    Send, {command}\n    Return\n")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _to_ahk_key(key: str) -> str:
    mapping = {
        "XButton1": "XButton1",
        "XButton2": "XButton2",
        "Clic milieu": "MButton",
        "Clic gauche": "LButton",
        "Clic droit": "RButton",
    }
    return mapping.get(key, key)
