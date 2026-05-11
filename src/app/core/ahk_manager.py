"""
Gestion du script AHK existant — lecture, modification en place, rechargement.
Chaque touche peut déclencher une séquence de commandes Revit et/ou de textes collés.

Format d'un item de séquence : {"type": "key"|"text", "value": str}
"""
from __future__ import annotations
import re
import subprocess
from pathlib import Path

from app.core import logger


ZONE_START = "; === REVIT MACRO TOOL - DEBUT ==="
ZONE_END   = "; === REVIT MACRO TOOL - FIN ==="

# Marqueurs dans le script AHK pour distinguer les items
_COMMENT_KEY  = "; [CMD]"
_COMMENT_TEXT = "; [TXT]"

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

# Type alias
SequenceItem = dict  # {"type": "key"|"text", "value": str}


def read_assignments(script_path: Path) -> dict[str, list[SequenceItem]]:
    """Lit les séquences depuis la zone gérée du script AHK."""
    if not script_path.exists():
        logger.warning(f"Script AHK introuvable : {script_path}")
        return {}
    content = script_path.read_text(encoding="utf-8")
    start = content.find(ZONE_START)
    end   = content.find(ZONE_END)
    if start == -1 or end == -1:
        logger.warning("Zone gérée introuvable dans le script — aucune assignation lue")
        return {}
    zone = content[start:end]
    assignments: dict[str, list[SequenceItem]] = {}
    block_pattern = re.compile(r"^(\S+)::\n(.*?)Return", re.MULTILINE | re.DOTALL)
    for block in block_pattern.finditer(zone):
        ahk_key = block.group(1)
        body    = block.group(2)
        items   = _parse_block_body(body)
        if items:
            ui_key = AHK_KEY_MAP_INV.get(ahk_key, ahk_key)
            assignments[ui_key] = items
    logger.success(f"Assignations lues depuis le script : {len(assignments)} touches")
    return assignments


def write_assignments(script_path: Path, assignments: dict[str, list[SequenceItem]]) -> None:
    """Met à jour la zone gérée dans le script existant. Le reste est préservé."""
    if not script_path.exists():
        _create_base_script(script_path)
    content    = script_path.read_text(encoding="utf-8")
    zone_block = _build_zone(assignments)
    start = content.find(ZONE_START)
    end   = content.find(ZONE_END)
    if start != -1 and end != -1:
        new_content = content[:start] + zone_block + content[end + len(ZONE_END):]
    else:
        new_content = content.rstrip() + "\n\n" + zone_block
    script_path.write_text(new_content, encoding="utf-8")
    total = sum(len(v) for v in assignments.values())
    logger.success(f"Script mis à jour : {len(assignments)} touches, {total} actions au total")


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


# ── Helpers internes ──────────────────────────────────────────────────────────

def _parse_block_body(body: str) -> list[SequenceItem]:
    items: list[SequenceItem] = []
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line == _COMMENT_KEY and i + 1 < len(lines):
            m = re.match(r"Send,\s+(.+)", lines[i + 1].strip())
            if m:
                items.append({"type": "key", "value": m.group(1)})
            i += 2
        elif line == _COMMENT_TEXT and i + 3 < len(lines):
            # Cherche la ligne Clipboard := "..."
            for j in range(i + 1, min(i + 5, len(lines))):
                m = re.match(r'Clipboard\s*:=\s*"(.*)"', lines[j].strip())
                if m:
                    items.append({"type": "text", "value": m.group(1)})
                    break
            i += 6  # saute le bloc clipboard complet
        else:
            i += 1
    return items


def _build_zone(assignments: dict[str, list[SequenceItem]]) -> str:
    blocks = [ZONE_START]
    for ui_key, items in assignments.items():
        if not items:
            continue
        ahk_key = AHK_KEY_MAP.get(ui_key, ui_key)
        lines = [f"{ahk_key}::"]
        for item in items:
            if item["type"] == "key":
                lines.append(f"    {_COMMENT_KEY}")
                lines.append(f"    Send, {item['value']}")
                lines.append(f"    Sleep, 100")
            elif item["type"] == "text":
                escaped = item["value"].replace('"', '""')
                lines.append(f"    {_COMMENT_TEXT}")
                lines.append(f'    oldClip := ClipboardAll')
                lines.append(f'    Clipboard := "{escaped}"')
                lines.append(f"    ClipWait, 1")
                lines.append(f"    Send, ^v")
                lines.append(f"    Sleep, 50")
                lines.append(f"    Clipboard := oldClip")
                lines.append(f"    Sleep, 100")
        lines.append("    Return")
        blocks.append("\n".join(lines))
    blocks.append(ZONE_END)
    return "\n\n".join(blocks) + "\n"


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
