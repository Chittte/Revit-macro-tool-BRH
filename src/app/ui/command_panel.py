"""
Panneau droit — liste des commandes Revit avec recherche.
Clic sur une commande = assignée à la touche/bouton actif.
"""
from __future__ import annotations
from typing import Callable
import customtkinter as ctk
from app.core.commands import RevitCommand, load, search


class CommandPanel(ctk.CTkFrame):
    def __init__(self, parent, on_assign: Callable[[str], None] | None = None, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self._on_assign = on_assign
        self._all_commands = load()
        self._active_key: str | None = None
        self._build()
        self._refresh("")

    def _build(self) -> None:
        ctk.CTkLabel(self, text="Commandes Revit", font=("Arial", 13, "bold")).pack(pady=(12, 6))

        # Touche sélectionnée
        self._key_label = ctk.CTkLabel(self, text="Aucune touche sélectionnée", font=("Arial", 11), text_color="gray")
        self._key_label.pack(pady=(0, 8))

        # Champ de recherche
        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._refresh(self._search_var.get()))
        ctk.CTkEntry(self, textvariable=self._search_var, placeholder_text="Rechercher...").pack(
            fill="x", padx=10, pady=(0, 6)
        )

        # Liste scrollable
        self._list_frame = ctk.CTkScrollableFrame(self)
        self._list_frame.pack(fill="both", expand=True, padx=6, pady=(0, 8))

        # Bouton désassigner
        self._unassign_btn = ctk.CTkButton(
            self,
            text="Retirer l'assignation",
            fg_color="#6b2b2b",
            hover_color="#8b3b3b",
            command=self._on_unassign,
        )
        self._unassign_btn.pack(fill="x", padx=10, pady=(0, 10))

    def _refresh(self, query: str) -> None:
        for widget in self._list_frame.winfo_children():
            widget.destroy()
        results = search(self._all_commands, query)
        for cmd in results:
            self._add_row(cmd)

    def _add_row(self, cmd: RevitCommand) -> None:
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
            command=lambda c=cmd: self._select_command(c),
        ).pack(fill="x")

    def _select_command(self, cmd: RevitCommand) -> None:
        if self._active_key and self._on_assign:
            self._on_assign(cmd.code)

    def _on_unassign(self) -> None:
        if self._active_key and self._on_assign:
            self._on_assign("")

    def set_active_key(self, key: str | None) -> None:
        self._active_key = key
        if key:
            self._key_label.configure(text=f"Touche : {key}", text_color="white")
        else:
            self._key_label.configure(text="Aucune touche sélectionnée", text_color="gray")
