"""
Affichage visuel de la souris — boutons cliquables pour assignation.
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
        self._assignments: dict[str, str] = {}
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

    def assign(self, button: str, command_code: str) -> None:
        self._assignments[button] = command_code
        if button in self._buttons:
            self._buttons[button].configure(
                text=f"{button}\n{command_code}",
                fg_color=COLOR_SELECTED if button == self._selected else COLOR_ASSIGNED,
            )

    def unassign(self, button: str) -> None:
        self._assignments.pop(button, None)
        if button in self._buttons:
            self._buttons[button].configure(
                text=button,
                fg_color=COLOR_SELECTED if button == self._selected else COLOR_DEFAULT,
            )

    def get_assignments(self) -> dict[str, str]:
        return dict(self._assignments)

    def load_assignments(self, assignments: dict[str, str]) -> None:
        for button, code in assignments.items():
            self.assign(button, code)
