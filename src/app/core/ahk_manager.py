"""
Gestion du script AHK existant — lecture, modification en place, rechargement.
Chaque touche peut déclencher une séquence de commandes Revit.
"""
from __future__ import annotations
import re
import subprocess
from pathlib import Path

from app.core import logger


ZONE_START = "; === REVIT MACRO TOOL - DEBUT ==="
ZONE_END   = "; === REVIT MACRO TOOL - FIN ==="

AHK_KEY_MAP = {
    "Clic gauche":  "LButton",
    "Clic milieu":  "MButton",
    "Clic droit":   "RButton",
    "XButton1":     "XButton1",
    "XButton2":     "XButton2",
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
    "`":            "``",
}

AHK_KEY_MAP_INV = {v: k for k, v in AHK_KEY_MAP.items()}


def read_assignments(script_path: Path) -> dict[str, list[str]]:
    """Lit les séquences de commandes depuis la zone gérée du script AHK."""
    if not script_path.exists():
        logger.warning(f"Script AHK introuvable : {script_path}")
        return {}
    content = script_path.read_text(encoding="utf-8")
    start = content.find(ZONE_START)
    end = content.find(ZONE_END)
    if start == -1 or end == -1:
        logger.warning("Zone gérée introuvable dans le script — aucune assignation lue")
        return {}
    zone = content[start:end]
    assignments: dict[str, list[str]] = {}
    # Pattern : KeyName::\n    Send, CMD1\n    Send, CMD2\n    Return
    block_pattern = re.compile(r"^(\S+)::\n(.*?)Return", re.MULTILINE | re.DOTALL)
    send_pattern  = re.compile(r"Send,\s+(\S+)")
    for block in block_pattern.finditer(zone):
        ahk_key  = block.group(1)
        body     = block.group(2)
        commands = send_pattern.findall(body)
        if commands:
            ui_key = AHK_KEY_MAP_INV.get(ahk_key, ahk_key)
            assignments[ui_key] = commands
    logger.success(f"Assignations lues depuis le script : {len(assignments)} touches")
    return assignments


def write_assignments(script_path: Path, assignments: dict[str, list[str]]) -> None:
    """Met à jour la zone gérée dans le script existant. Le reste est préservé."""
    if not script_path.exists():
        _create_base_script(script_path)

    content = script_path.read_text(encoding="utf-8")
    zone_block = _build_zone(assignments)

    start = content.find(ZONE_START)
    end   = content.find(ZONE_END)

    if start != -1 and end != -1:
        new_content = content[:start] + zone_block + content[end + len(ZONE_END):]
    else:
        new_content = content.rstrip() + "\n\n" + zone_block

    script_path.write_text(new_content, encoding="utf-8")
    total_cmds = sum(len(v) for v in assignments.values())
    logger.success(f"Script mis à jour : {len(assignments)} touches, {total_cmds} commandes au total")


def reload_script(script_path: Path) -> None:
    ahk_exe = _find_ahk()
    if not ahk_exe:
        logger.warning("AutoHotkey introuvable — rechargement ignoré")
        return
    try:
        subprocess.Popen([ahk_exe, "/restart", str(script_path)],
                         creationflags=subprocess.CREATE_NO_WINDOW)
        logger.success("Script AHK rechargé")
    except Exception as e:
        logger.error("Échec rechargement AHK", e)


def launch_script(script_path: Path) -> None:
    ahk_exe = _find_ahk()
    if not ahk_exe:
        logger.warning("AutoHotkey introuvable — installez AHK v1.1")
        return
    try:
        subprocess.Popen([ahk_exe, str(script_path)],
                         creationflags=subprocess.CREATE_NO_WINDOW)
        logger.success(f"Script AHK lancé : {script_path}")
    except Exception as e:
        logger.error("Échec lancement AHK", e)


def _build_zone(assignments: dict[str, list[str]]) -> str:
    lines = [ZONE_START + "\n"]
    for ui_key, commands in assignments.items():
        if not commands:
            continue
        ahk_key = AHK_KEY_MAP.get(ui_key, ui_key)
        block = [f"{ahk_key}::"]
        for cmd in commands:
            block.append(f"    Send, {cmd}")
            block.append(f"    Sleep, 100")
        block.append(f"    Return")
        lines.append("\n".join(block))
    lines.append(ZONE_END)
    return "\n\n".join(lines) + "\n"


def _create_base_script(script_path: Path) -> None:
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(
        "#Requires AutoHotkey v1.1\n"
        "#SingleInstance Force\n"
        "#NoEnv\n"
        "SetWorkingDir %A_ScriptDir%\n\n",
        encoding="utf-8",
    )
    logger.info(f"Nouveau script AHK créé : {script_path}")


def _find_ahk() -> str | None:
    candidates = [
        r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
        r"C:\Program Files\AutoHotkey\v1\AutoHotkey.exe",
        r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe",
    ]
    for path in candidates:
        if Path(path).exists():
            return path
    return None
