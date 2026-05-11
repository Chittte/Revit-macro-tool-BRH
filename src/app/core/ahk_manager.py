"""
Génère et gère le script AHK multi-profils.
AHK gère PgUp/PgDn et écrit le profil actif dans _rmt_profile.txt.
Python lit ce fichier pour synchroniser la vue compacte.
"""
from __future__ import annotations
import re
import subprocess
from pathlib import Path

from app.core import logger

SequenceItem = dict
ZONE_START = "; === REVIT MACRO TOOL - DEBUT ==="
ZONE_END   = "; === REVIT MACRO TOOL - FIN ==="

AHK_KEY_MAP = {
    "Clic gauche": "LButton", "Clic milieu": "MButton", "Clic droit": "RButton",
    "XButton1": "XButton1", "XButton2": "XButton2",
    "Esc": "Escape", "Backspace": "Backspace", "Tab": "Tab", "Caps": "CapsLock",
    "Enter": "Enter", "Shift": "Shift", "Ctrl": "Ctrl", "Alt": "Alt",
    "AltGr": "AltGr", "Win": "LWin", "Menu": "AppsKey", "Space": "Space",
    "`": "``",
}
AHK_KEY_MAP_INV = {v: k for k, v in AHK_KEY_MAP.items()}


def write_profiles(script_path: Path, profiles: list[dict]) -> None:
    """Écrit le script AHK complet (header + zone) — remplace le fichier entier."""
    script_path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "#Requires AutoHotkey v1.1\n"
        "#SingleInstance Force\n"
        "#NoEnv\n"
        "SetWorkingDir %A_ScriptDir%\n\n"
    )
    script_path.write_text(header + _build_zone(profiles, script_path), encoding="utf-8")
    logger.success(f"Script AHK mis à jour : {len(profiles)} profil(s)")


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


def read_active_profile_index(script_path: Path) -> int:
    """Lit l'index du profil actif écrit par AHK (1-based)."""
    tracker = script_path.parent / "_rmt_profile.txt"
    try:
        return int(tracker.read_text(encoding="utf-8").strip())
    except Exception:
        return 1


# ── Génération du script ─────────────────────────────────────────────────────

def _build_zone(profiles: list[dict], script_path: Path) -> str:
    count     = len(profiles)
    tracker   = str(script_path.parent / "_rmt_profile.txt").replace("\\", "\\\\")
    lines     = [ZONE_START]

    # Variables globales
    lines += [
        f"global _rmt_idx   := 1",
        f"global _rmt_count := {count}",
        "",
    ]

    # Navigation PgUp / PgDn (actif seulement dans Revit)
    lines += [
        "#IfWinActive Autodesk Revit",
        "PgUp::",
        "    _rmt_idx := (_rmt_idx > 1) ? _rmt_idx - 1 : _rmt_count",
        f'    FileDelete, {tracker}',
        f'    FileAppend, %_rmt_idx%, {tracker}',
        "    return",
        "",
        "PgDn::",
        "    _rmt_idx := (_rmt_idx < _rmt_count) ? _rmt_idx + 1 : 1",
        f'    FileDelete, {tracker}',
        f'    FileAppend, %_rmt_idx%, {tracker}',
        "    return",
        "",
    ]

    # Collecter toutes les touches assignées dans tous les profils
    all_keys: set[str] = set()
    for p in profiles:
        all_keys.update(p.get("assignments", {}).keys())

    # Générer un hotkey par touche avec branchement par profil
    for ui_key in sorted(all_keys):
        ahk_key = AHK_KEY_MAP.get(ui_key, ui_key)
        lines.append(f"{ahk_key}::")
        for idx, profile in enumerate(profiles, start=1):
            assignments = profile.get("assignments", {})
            seq = assignments.get(ui_key, [])
            if not seq:
                continue
            condition = "if" if idx == 1 else "else if"
            lines.append(f"    {condition} (_rmt_idx == {idx})  ; {profile['name']}")
            lines.append("    {")
            for item in seq:
                if item["type"] == "key":
                    lines.append(f"        Send, {item['value']}")
                    lines.append(f"        Sleep, 100")
                elif item["type"] == "text":
                    escaped = item["value"].replace('"', '""')
                    lines.append(f'        oldClip := ClipboardAll')
                    lines.append(f'        Clipboard := "{escaped}"')
                    lines.append(f'        ClipWait, 1')
                    lines.append(f'        Send, ^v')
                    lines.append(f'        Sleep, 50')
                    lines.append(f'        Clipboard := oldClip')
                    lines.append(f'        Sleep, 100')
            lines.append("    }")
        lines.append("    return")
        lines.append("")

    lines += ["#IfWinActive", "", ZONE_END]
    return "\n".join(lines) + "\n"


def _create_base_script(script_path: Path) -> None:
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(
        "#Requires AutoHotkey v1.1\n#SingleInstance Force\n#NoEnv\nSetWorkingDir %A_ScriptDir%\n\n",
        encoding="utf-8",
    )
    logger.info(f"Nouveau script AHK créé : {script_path}")


def _find_ahk() -> str | None:
    for p in [
        r"C:\Program Files\AutoHotkey\AutoHotkey.exe",
        r"C:\Program Files\AutoHotkey\v1\AutoHotkey.exe",
        r"C:\Program Files (x86)\AutoHotkey\AutoHotkey.exe",
    ]:
        if Path(p).exists():
            return p
    return None
