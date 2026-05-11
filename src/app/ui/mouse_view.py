"""
Affichage visuel de la souris — boutons cliquables pour assignation.
"""
import customtkinter as ctk


MOUSE_BUTTONS = ["Clic gauche", "Clic milieu", "Clic droit", "XButton1", "XButton2"]


class MouseView(ctk.CTkFrame):
    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self._selected_button: str | None = None
        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(self, text="Souris", font=("Arial", 12, "bold")).pack(anchor="w", padx=5, pady=(5, 2))
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=5, pady=5)
        for btn_name in MOUSE_BUTTONS:
            btn = ctk.CTkButton(
                row,
                text=btn_name,
                width=100,
                height=35,
                font=("Arial", 10),
                command=lambda b=btn_name: self._on_button_click(b),
            )
            btn.pack(side="left", padx=3)

    def _on_button_click(self, button: str) -> None:
        # TODO: ouvrir la sélection de commande Revit pour ce bouton
        self._selected_button = button
