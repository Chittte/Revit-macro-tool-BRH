"""
Affichage visuel du clavier — QWERTY.
Chaque touche peut avoir une séquence de commandes Revit et/ou textes.
"""
from __future__ import annotations
from typing import Callable
import customtkinter as ctk

SequenceItem = dict  # {"type": "key"|"text", "value": str}

QWERTY_ROWS = [
    ["Esc", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
    ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Backspace"],
    ["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "\\"],
    ["Caps", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", "Enter"],
    ["Shift", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "Shift"],
    ["Ctrl", "Win", "Alt", "Space", "AltGr", "Win", "Menu", "Ctrl"],
]

WIDE_KEYS      = {"Backspace", "Tab", "Caps", "Enter", "Shift", "Space", "Ctrl", "Win", "Alt", "AltGr", "Menu"}
COLOR_DEFAULT  = "#2b2b2b"
COLOR_SELECTED = "#1f6aa5"
COLOR_ASSIGNED = "#2d6e3e"


class KeyboardView(ctk.CTkFrame):
    def __init__(self, parent, on_select: Callable[[str], None] | None = None, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self._on_select = on_select
        self._selected: str | None = None
        self._assignments: dict[str, list[SequenceItem]] = {}
        self._buttons: dict[str, ctk.CTkButton] = {}
        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(self, text="Clavier", font=("Arial", 12, "bold")).pack(anchor="w", padx=8, pady=(6, 2))
        for row in QWERTY_ROWS:
            row_frame = ctk.CTkFrame(self, fg_color="transparent")
            row_frame.pack(fill="x", pady=1, padx=6)
            for key in row:
                width = 68 if key in WIDE_KEYS else 38
                btn = ctk.CTkButton(
                    row_frame, text=key, width=width, height=34, font=("Arial", 9),
                    fg_color=COLOR_DEFAULT, hover_color="#3a3a3a",
                    command=lambda k=key: self._on_click(k),
                )
                btn.pack(side="left", padx=1)
                if key not in self._buttons:
                    self._buttons[key] = btn

    def _on_click(self, key: str) -> None:
        self._set_selected(key)
        if self._on_select:
            self._on_select(key)

    def _set_selected(self, key: str) -> None:
        if self._selected and self._selected in self._buttons:
            color = COLOR_ASSIGNED if self._selected in self._assignments else COLOR_DEFAULT
            self._buttons[self._selected].configure(fg_color=color)
        self._selected = key
        if key in self._buttons:
            self._buttons[key].configure(fg_color=COLOR_SELECTED)

    def set_commands(self, key: str, sequence: list[SequenceItem]) -> None:
        if sequence:
            self._assignments[key] = sequence
        else:
            self._assignments.pop(key, None)
        if key in self._buttons:
            self._buttons[key].configure(
                text=_btn_label(key, sequence),
                fg_color=COLOR_SELECTED if key == self._selected else (COLOR_ASSIGNED if sequence else COLOR_DEFAULT),
            )

    def get_commands(self, key: str) -> list[SequenceItem]:
        return list(self._assignments.get(key, []))

    def get_assignments(self) -> dict[str, list[SequenceItem]]:
        return {k: list(v) for k, v in self._assignments.items()}

    def load_assignments(self, assignments: dict[str, list[SequenceItem]]) -> None:
        for key, seq in assignments.items():
            if key in self._buttons:
                self.set_commands(key, seq)


def _btn_label(key: str, seq: list[SequenceItem]) -> str:
    if not seq:
        return key
    first = seq[0]["value"] if seq[0]["type"] == "key" else "TXT"
    if len(seq) == 1:
        return f"{key}\n{first}" if len(key) <= 4 else key
    return f"{key}\n{first}+{len(seq)-1}"
