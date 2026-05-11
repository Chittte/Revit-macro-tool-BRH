"""
Fenêtre compacte flottante — style v1 MacroProfils.
Affiche les assignations actives, toujours au-dessus, draggable.
"""
from __future__ import annotations
from typing import Callable
import customtkinter as ctk

SequenceItem = dict


class CompactWindow(ctk.CTkToplevel):
    def __init__(self, parent, on_configure: Callable | None = None) -> None:
        super().__init__(parent)
        self._on_configure = on_configure
        self._assignments: dict[str, list[SequenceItem]] = {}
        self._drag_x = 0
        self._drag_y = 0

        self.overrideredirect(True)          # Pas de barre de titre Windows
        self.attributes("-topmost", True)    # Toujours au-dessus
        self.configure(fg_color="#1E1E1E")
        self.geometry("210x60+20+20")

        self._build()
        self._bind_drag()

    def _build(self) -> None:
        # Barre de titre custom
        title_bar = ctk.CTkFrame(self, fg_color="#252526", height=26, corner_radius=0)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        ctk.CTkLabel(title_bar, text="REVIT MACRO TOOL",
                     font=("Segoe UI", 8, "bold"), text_color="#888").pack(side="left", padx=8)
        ctk.CTkButton(title_bar, text="x", width=22, height=22,
                      font=("Segoe UI", 9, "bold"),
                      fg_color="transparent", hover_color="#c0392b",
                      text_color="#FF6B6B",
                      command=self.withdraw).pack(side="right", padx=2, pady=2)
        self._bind_drag_widget(title_bar)

        # Zone des assignations
        self._content = ctk.CTkFrame(self, fg_color="transparent")
        self._content.pack(fill="both", expand=True, padx=6, pady=(4, 0))

        # Bouton configurer
        ctk.CTkButton(self, text="⚙ Configurer", height=24,
                      font=("Segoe UI", 9), fg_color="#252526",
                      hover_color="#3a3a3a", text_color="#4FC3F7",
                      corner_radius=0, command=self._open_config).pack(fill="x")

    def _bind_drag(self) -> None:
        self._bind_drag_widget(self)

    def _bind_drag_widget(self, widget) -> None:
        widget.bind("<ButtonPress-1>",   self._start_drag)
        widget.bind("<B1-Motion>",       self._do_drag)

    def _start_drag(self, event) -> None:
        self._drag_x = event.x_root - self.winfo_x()
        self._drag_y = event.y_root - self.winfo_y()

    def _do_drag(self, event) -> None:
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.geometry(f"+{x}+{y}")

    def _open_config(self) -> None:
        if self._on_configure:
            self._on_configure()

    def update_assignments(self, assignments: dict[str, list[SequenceItem]]) -> None:
        self._assignments = assignments
        self._refresh()

    def _refresh(self) -> None:
        for w in self._content.winfo_children():
            w.destroy()

        assigned = {k: v for k, v in self._assignments.items() if v}
        if not assigned:
            ctk.CTkLabel(self._content, text="Aucune assignation",
                         text_color="#555", font=("Segoe UI", 9)).pack(pady=4)
            self._resize(60)
            return

        for key, seq in assigned.items():
            row = ctk.CTkFrame(self._content, fg_color="transparent")
            row.pack(fill="x", pady=1)
            # Nom de la touche
            ctk.CTkLabel(row, text=key, font=("Segoe UI", 9, "bold"),
                         text_color="#4FC3F7", width=70, anchor="w").pack(side="left")
            # Résumé de la séquence
            summary = _sequence_summary(seq)
            ctk.CTkLabel(row, text=summary, font=("Segoe UI", 9),
                         text_color="#cccccc", anchor="w").pack(side="left", fill="x", expand=True)

        height = 26 + len(assigned) * 22 + 28 + 12
        self._resize(height)

    def _resize(self, height: int) -> None:
        x = self.winfo_x()
        y = self.winfo_y()
        self.geometry(f"210x{height}+{x}+{y}")


def _sequence_summary(seq: list[SequenceItem]) -> str:
    parts = []
    for item in seq:
        if item["type"] == "key":
            parts.append(item["value"].upper())
        else:
            txt = item["value"]
            parts.append(f'"{txt[:10]}…"' if len(txt) > 10 else f'"{txt}"')
    return " → ".join(parts) if parts else ""
