"""
Affichage visuel du clavier — QWERTY.
Chaque touche est un bouton cliquable pour assigner une commande Revit.
"""
import customtkinter as ctk


QWERTY_ROWS = [
    ["Esc", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
    ["`", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Backspace"],
    ["Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", "\\"],
    ["Caps", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'", "Enter"],
    ["Shift", "Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "Shift"],
    ["Ctrl", "Win", "Alt", "Space", "AltGr", "Win", "Menu", "Ctrl"],
]


class KeyboardView(ctk.CTkFrame):
    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self._selected_key: str | None = None
        self._buttons: dict[str, ctk.CTkButton] = {}
        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(self, text="Clavier", font=("Arial", 12, "bold")).pack(anchor="w", padx=5, pady=(5, 2))
        for row in QWERTY_ROWS:
            row_frame = ctk.CTkFrame(self, fg_color="transparent")
            row_frame.pack(fill="x", pady=1, padx=5)
            for key in row:
                width = 70 if key in ("Backspace", "Enter", "Shift", "Space") else 40
                btn = ctk.CTkButton(
                    row_frame,
                    text=key,
                    width=width,
                    height=35,
                    font=("Arial", 10),
                    command=lambda k=key: self._on_key_click(k),
                )
                btn.pack(side="left", padx=1)
                self._buttons[key] = btn

    def _on_key_click(self, key: str) -> None:
        # TODO: ouvrir la sélection de commande Revit pour cette touche
        self._selected_key = key
