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

# Correspondance touches UI → noms AHK
AHK_KEY_MAP = {
    # Souris
    "Clic gauche":  "LButton",
    "Clic milieu":  "MButton",
    "Clic droit":   "RButton",
    "XButton1":     "XButton1",
    "XButton2":     "XButton2",
    # Touches spéciales clavier
    "Esc":          "Escape",
    "Backspace":    "Backspace",
    "Tab":          "Tab",
    "Caps":         "CapsLock",
    "Enter":        "Enter",
    "Shift":        "Shift",
    "Ctrl":         "Ctrl",
    "Alt":          "Alt",
    "AltGr":        "AltGr",
    "Win":          "LWin",
    "Menu":         "AppsKey",
    "Space":        "Space",
    # Touches dont le caractère AHK doit être échappé
    "`":            "``",
}


def generate(assignments: dict[str, str], output_path: Path) -> None:
    lines = [AHK_HEADER]
    for key, command in assignments.items():
        ahk_key = _to_ahk_key(key)
        lines.append(f"{ahk_key}::\n    Send, {command}\n    Return\n")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _to_ahk_key(key: str) -> str:
    return AHK_KEY_MAP.get(key, key)
