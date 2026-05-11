"""
Panneau droit — gestion de la séquence de commandes pour la touche sélectionnée.
Permet d'ajouter, retirer et réordonner plusieurs commandes sur un même bouton.
"""
from __future__ import annotations
from typing import Callable
import customtkinter as ctk
from app.core.commands import RevitCommand, load, search


class CommandPanel(ctk.CTkFrame):
    def __init__(self, parent, on_change: Callable[[list[str]], None] | None = None, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self._on_change = on_change
        self._all_commands = load()
        self._active_key: str | None = None
        self._sequence: list[str] = []
        self._build()
        self._refresh_search("")

    def _build(self) -> None:
        # Touche active
        ctk.CTkLabel(self, text="Commandes Revit", font=("Arial", 13, "bold")).pack(pady=(12, 2))
        self._key_label = ctk.CTkLabel(self, text="Aucune touche sélectionnée",
                                        font=("Arial", 11), text_color="gray")
        self._key_label.pack(pady=(0, 8))

        # Séquence assignée
        ctk.CTkLabel(self, text="Séquence assignée :", font=("Arial", 11, "bold")).pack(anchor="w", padx=10)
        self._seq_frame = ctk.CTkFrame(self, fg_color="#1e1e1e", corner_radius=6)
        self._seq_frame.pack(fill="x", padx=10, pady=(4, 6))

        ctk.CTkButton(self, text="Tout effacer", height=26, fg_color="#6b2b2b",
                      hover_color="#8b3b3b", command=self._clear_all).pack(fill="x", padx=10, pady=(0, 8))

        # Séparateur
        ctk.CTkFrame(self, height=1, fg_color="#444").pack(fill="x", padx=10, pady=(0, 8))

        # Recherche + ajout
        ctk.CTkLabel(self, text="Ajouter une commande :", font=("Arial", 11, "bold")).pack(anchor="w", padx=10)
        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._refresh_search(self._search_var.get()))
        ctk.CTkEntry(self, textvariable=self._search_var,
                     placeholder_text="Rechercher...").pack(fill="x", padx=10, pady=(4, 4))

        self._list_frame = ctk.CTkScrollableFrame(self)
        self._list_frame.pack(fill="both", expand=True, padx=6, pady=(0, 8))

    # ── Séquence ────────────────────────────────────────────────────────────────

    def _refresh_sequence(self) -> None:
        for w in self._seq_frame.winfo_children():
            w.destroy()
        if not self._sequence:
            ctk.CTkLabel(self._seq_frame, text="(aucune)", text_color="gray",
                         font=("Arial", 10)).pack(pady=4)
            return
        for i, code in enumerate(self._sequence):
            row = ctk.CTkFrame(self._seq_frame, fg_color="transparent")
            row.pack(fill="x", padx=4, pady=2)
            # Flèches haut/bas
            ctk.CTkButton(row, text="▲", width=22, height=22, font=("Arial", 9),
                          fg_color="#333", hover_color="#555",
                          command=lambda idx=i: self._move(idx, -1)).pack(side="left", padx=(0, 2))
            ctk.CTkButton(row, text="▼", width=22, height=22, font=("Arial", 9),
                          fg_color="#333", hover_color="#555",
                          command=lambda idx=i: self._move(idx, 1)).pack(side="left", padx=(0, 6))
            # Numéro + code
            ctk.CTkLabel(row, text=f"{i+1}.", width=20, font=("Arial", 10),
                         text_color="#888").pack(side="left")
            ctk.CTkLabel(row, text=code, font=("Arial", 11, "bold"),
                         text_color="#4FC3F7").pack(side="left", padx=4)
            # Supprimer
            ctk.CTkButton(row, text="✕", width=24, height=22, font=("Arial", 9),
                          fg_color="#6b2b2b", hover_color="#8b3b3b",
                          command=lambda idx=i: self._remove(idx)).pack(side="right")

    def _move(self, idx: int, direction: int) -> None:
        new_idx = idx + direction
        if 0 <= new_idx < len(self._sequence):
            self._sequence[idx], self._sequence[new_idx] = self._sequence[new_idx], self._sequence[idx]
            self._refresh_sequence()
            self._emit()

    def _remove(self, idx: int) -> None:
        self._sequence.pop(idx)
        self._refresh_sequence()
        self._emit()

    def _clear_all(self) -> None:
        self._sequence.clear()
        self._refresh_sequence()
        self._emit()

    def _add_command(self, code: str) -> None:
        if not self._active_key:
            return
        self._sequence.append(code)
        self._refresh_sequence()
        self._emit()

    def _emit(self) -> None:
        if self._on_change:
            self._on_change(list(self._sequence))

    # ── Recherche ───────────────────────────────────────────────────────────────

    def _refresh_search(self, query: str) -> None:
        for w in self._list_frame.winfo_children():
            w.destroy()
        for cmd in search(self._all_commands, query):
            self._add_search_row(cmd)

    def _add_search_row(self, cmd: RevitCommand) -> None:
        row = ctk.CTkFrame(self._list_frame, fg_color="transparent")
        row.pack(fill="x", pady=1)
        ctk.CTkButton(
            row,
            text=f"{cmd.code}  —  {cmd.name}",
            anchor="w",
            font=("Arial", 11),
            fg_color="transparent",
            hover_color="#1f6aa5",
            height=30,
            command=lambda c=cmd: self._add_command(c.code),
        ).pack(fill="x")

    # ── Interface publique ───────────────────────────────────────────────────────

    def set_active_key(self, key: str | None, commands: list[str] | None = None) -> None:
        self._active_key = key
        self._sequence = list(commands or [])
        if key:
            self._key_label.configure(text=f"Touche : {key}", text_color="white")
        else:
            self._key_label.configure(text="Aucune touche sélectionnée", text_color="gray")
        self._refresh_sequence()
