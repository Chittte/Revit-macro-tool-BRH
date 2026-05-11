"""
Affichage visuel du clavier — QWERTY.
Chaque touche est cliquable pour assigner une commande Revit.
"""
from __future__ import annotations
from typing import Callable
import customtkinter as ctk


QWERTY_ROWS = [
    ["Esc", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
    ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Backspace"],
    ["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "\\"],
    ["Caps", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", "Enter"],
    ["Shift", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "Shift"],
    ["Ctrl", "Win", "Alt", "Space", "AltGr", "Win", "Menu", "Ctrl"],
]

WIDE_KEYS = {"Backspace", "Tab", "Caps", "Enter", "Shift", "Space", "Ctrl", "Win", "Alt", "AltGr", "Menu"}

COLOR_DEFAULT  = "#2b2b2b"
COLOR_SELECTED = "#1f6aa5"
COLOR_ASSIGNED = "#2d6e3e"


class KeyboardView(ctk.CTkFrame):
    def __init__(self, parent, on_select: Callable[[str], None] | None = None, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self._on_select = on_select
        self._selected: str | None = None
        self._assignments: dict[str, str] = {}
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
                    row_frame,
                    text=key,
                    width=width,
                    height=34,
                    font=("Arial", 9),
                    fg_color=COLOR_DEFAULT,
                    hover_color="#3a3a3a",
                    command=lambda k=key: self._on_click(k),
                )
                btn.pack(side="left", padx=1)
                # Pour les touches dupliquées (ex: 2x Shift), on garde la première occurrence
                if key not in self._buttons:
                    self._buttons[key] = btn

    def _on_click(self, key: str) -> None:
        self._set_selected(key)
        if self._on_select:
            self._on_select(key)

    def _set_selected(self, key: str) -> None:
        # Désélectionner l'ancienne
        if self._selected and self._selected in self._buttons:
            color = COLOR_ASSIGNED if self._selected in self._assignments else COLOR_DEFAULT
            self._buttons[self._selected].configure(fg_color=color)
        self._selected = key
        if key in self._buttons:
            self._buttons[key].configure(fg_color=COLOR_SELECTED)

    def assign(self, key: str, command_code: str) -> None:
        self._assignments[key] = command_code
        if key in self._buttons:
            label = key if len(key) > 2 else f"{key}\n{command_code}"
            self._buttons[key].configure(
                text=label,
                fg_color=COLOR_SELECTED if key == self._selected else COLOR_ASSIGNED,
            )

    def unassign(self, key: str) -> None:
        self._assignments.pop(key, None)
        if key in self._buttons:
            self._buttons[key].configure(
                text=key,
                fg_color=COLOR_SELECTED if key == self._selected else COLOR_DEFAULT,
            )

    def get_assignments(self) -> dict[str, str]:
        return dict(self._assignments)

    def load_assignments(self, assignments: dict[str, str]) -> None:
        for key, code in assignments.items():
            self.assign(key, code)
