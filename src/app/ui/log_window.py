"""
Fenêtre de logs flottante — affiche les événements en temps réel.
Peut rester ouverte en permanence pendant les tests.
"""
from __future__ import annotations
import customtkinter as ctk
from app.core import logger


LEVEL_COLORS = {
    "INFO":    "#c8c8c8",
    "SUCCESS": "#4caf50",
    "WARNING": "#ff9800",
    "ERROR":   "#f44336",
}

LEVEL_LABELS = {
    "INFO":    "ℹ INFO",
    "SUCCESS": "✓ OK",
    "WARNING": "⚠ AVERT",
    "ERROR":   "✗ ERREUR",
}


class LogWindow(ctk.CTkToplevel):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.title("Revit Macro Tool — Logs")
        self.geometry("720x440")
        self.minsize(500, 300)
        # Reste au-dessus de la fenêtre principale
        self.attributes("-topmost", True)
        self._filter_level: str | None = None
        self._build_ui()
        self._load_existing()
        logger.subscribe(self._on_new_entry)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        # Barre de filtres
        bar = ctk.CTkFrame(self, height=40)
        bar.pack(fill="x", padx=8, pady=(8, 4))
        bar.pack_propagate(False)

        ctk.CTkLabel(bar, text="Filtrer :").pack(side="left", padx=(8, 4))
        for level in ("INFO", "SUCCESS", "WARNING", "ERROR"):
            color = LEVEL_COLORS[level]
            ctk.CTkButton(
                bar,
                text=LEVEL_LABELS[level],
                width=90,
                height=28,
                fg_color=color if level != "INFO" else "#555",
                text_color="white",
                hover_color="#444",
                command=lambda l=level: self._set_filter(l),
            ).pack(side="left", padx=3)

        ctk.CTkButton(
            bar,
            text="Tout",
            width=60,
            height=28,
            fg_color="#333",
            hover_color="#444",
            command=lambda: self._set_filter(None),
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            bar,
            text="Effacer",
            width=70,
            height=28,
            fg_color="#333",
            hover_color="#555",
            command=self._clear,
        ).pack(side="right", padx=8)

        # Zone de logs scrollable
        self._log_box = ctk.CTkScrollableFrame(self)
        self._log_box.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def _load_existing(self) -> None:
        for entry in logger.get_all():
            self._add_entry(entry)

    def _on_new_entry(self, entry: dict) -> None:
        # Appelé depuis un thread — on passe par after() pour rester thread-safe
        try:
            self.after(0, self._add_entry, entry)
        except Exception:
            pass

    def _add_entry(self, entry: dict) -> None:
        if self._filter_level and entry["level"] != self._filter_level:
            return
        color = LEVEL_COLORS.get(entry["level"], "#c8c8c8")
        label_text = LEVEL_LABELS.get(entry["level"], entry["level"])
        row = ctk.CTkFrame(self._log_box, fg_color="transparent")
        row.pack(fill="x", pady=1)
        ctk.CTkLabel(
            row,
            text=f"{entry['time']}",
            font=("Courier", 10),
            text_color="#888",
            width=65,
            anchor="w",
        ).pack(side="left")
        ctk.CTkLabel(
            row,
            text=label_text,
            font=("Courier", 10, "bold"),
            text_color=color,
            width=75,
            anchor="w",
        ).pack(side="left", padx=(4, 8))
        ctk.CTkLabel(
            row,
            text=entry["msg"],
            font=("Courier", 10),
            text_color=color,
            anchor="w",
            wraplength=520,
            justify="left",
        ).pack(side="left", fill="x", expand=True)
        # Auto-scroll vers le bas
        self._log_box._parent_canvas.yview_moveto(1.0)

    def _set_filter(self, level: str | None) -> None:
        self._filter_level = level
        for widget in self._log_box.winfo_children():
            widget.destroy()
        for entry in logger.get_all():
            self._add_entry(entry)

    def _clear(self) -> None:
        for widget in self._log_box.winfo_children():
            widget.destroy()

    def _on_close(self) -> None:
        logger.unsubscribe(self._on_new_entry)
        self.destroy()
