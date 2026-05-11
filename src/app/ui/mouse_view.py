"""
Affichage visuel de la souris — boutons cliquables pour assignation.
Chaque bouton peut avoir une séquence de commandes Revit.
"""
from __future__ import annotations
from typing import Callable
import customtkinter as ctk


MOUSE_BUTTONS = ["Clic gauche", "Clic milieu", "Clic droit", "XButton1", "XButton2"]

COLOR_DEFAULT  = "#2b2b2b"
COLOR_SELECTED = "#1f6aa5"
COLOR_ASSIGNED = "#2d6e3e"


class MouseView(ctk.CTkFrame):
    def __init__(self, parent, on_select: Callable[[str], None] | None = None, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self._on_select = on_select
        self._selected: str | None = None
        self._assignments: dict[str, list[str]] = {}
        self._buttons: dict[str, ctk.CTkButton] = {}
        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(self, text="Souris", font=("Arial", 12, "bold")).pack(anchor="w", padx=8, pady=(6, 2))
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=6, pady=(0, 6))
        for name in MOUSE_BUTTONS:
            btn = ctk.CTkButton(
                row,
                text=name,
                width=110,
                height=40,
                font=("Arial", 10),
                fg_color=COLOR_DEFAULT,
                hover_color="#3a3a3a",
                command=lambda b=name: self._on_click(b),
            )
            btn.pack(side="left", padx=3)
            self._buttons[name] = btn

    def _on_click(self, button: str) -> None:
        self._set_selected(button)
        if self._on_select:
            self._on_select(button)

    def _set_selected(self, button: str) -> None:
        if self._selected and self._selected in self._buttons:
            color = COLOR_ASSIGNED if self._selected in self._assignments else COLOR_DEFAULT
            self._buttons[self._selected].configure(fg_color=color)
        self._selected = button
        self._buttons[button].configure(fg_color=COLOR_SELECTED)

    def set_commands(self, button: str, commands: list[str]) -> None:
        if commands:
            self._assignments[button] = commands
        else:
            self._assignments.pop(button, None)
        if button in self._buttons:
            label = _mouse_label(button, commands)
            self._buttons[button].configure(
                text=label,
                fg_color=COLOR_SELECTED if button == self._selected else (COLOR_ASSIGNED if commands else COLOR_DEFAULT),
            )

    def get_commands(self, button: str) -> list[str]:
        return list(self._assignments.get(button, []))

    def get_assignments(self) -> dict[str, list[str]]:
        return {k: list(v) for k, v in self._assignments.items()}

    def load_assignments(self, assignments: dict[str, list[str]]) -> None:
        for button, commands in assignments.items():
            if button in self._buttons:
                self.set_commands(button, commands)


def _mouse_label(button: str, commands: list[str]) -> str:
    if not commands:
        return button
    if len(commands) == 1:
        return f"{button}\n{commands[0]}"
    return f"{button}\n{commands[0]}+{len(commands)-1}"
