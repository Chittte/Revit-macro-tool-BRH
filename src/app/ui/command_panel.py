"""
Panneau droit — gestion de la séquence pour la touche sélectionnée.
Chaque item peut être une commande Revit (CMD) ou du texte à coller (TXT).
"""
from __future__ import annotations
from typing import Callable
import customtkinter as ctk
from app.core.commands import RevitCommand, load, search

SequenceItem = dict  # {"type": "key"|"text", "value": str}

COLOR_CMD  = "#1f6aa5"
COLOR_TEXT = "#7b4fa6"


class CommandPanel(ctk.CTkFrame):
    def __init__(self, parent, on_change: Callable[[list[SequenceItem]], None] | None = None, **kwargs) -> None:
        super().__init__(parent, **kwargs)
        self._on_change = on_change
        self._all_commands = load()
        self._active_key: str | None = None
        self._sequence: list[SequenceItem] = []
        self._build()
        self._refresh_search("")

    def _build(self) -> None:
        ctk.CTkLabel(self, text="Séquence", font=("Arial", 13, "bold")).pack(pady=(12, 2))
        self._key_label = ctk.CTkLabel(self, text="Aucune touche sélectionnée",
                                        font=("Arial", 11), text_color="gray")
        self._key_label.pack(pady=(0, 6))

        # Zone séquence
        self._seq_frame = ctk.CTkFrame(self, fg_color="#1a1a1a", corner_radius=6)
        self._seq_frame.pack(fill="x", padx=10, pady=(0, 4))

        ctk.CTkButton(self, text="Tout effacer", height=24, fg_color="#6b2b2b",
                      hover_color="#8b3b3b", command=self._clear_all).pack(fill="x", padx=10, pady=(0, 8))

        ctk.CTkFrame(self, height=1, fg_color="#444").pack(fill="x", padx=10, pady=(0, 6))

        # Onglets — CMD / TXT
        tabs = ctk.CTkFrame(self, fg_color="transparent")
        tabs.pack(fill="x", padx=10, pady=(0, 4))
        self._tab_var = ctk.StringVar(value="cmd")
        ctk.CTkSegmentedButton(tabs, values=["Commande Revit", "Texte à coller"],
                                variable=self._tab_var,
                                command=self._on_tab_change).pack(fill="x")

        # Contenu onglet CMD
        self._cmd_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._search_var = ctk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._refresh_search(self._search_var.get()))
        ctk.CTkEntry(self._cmd_frame, textvariable=self._search_var,
                     placeholder_text="Rechercher une commande...").pack(fill="x", padx=0, pady=(0, 4))
        self._list_frame = ctk.CTkScrollableFrame(self._cmd_frame)
        self._list_frame.pack(fill="both", expand=True)
        self._cmd_frame.pack(fill="both", expand=True, padx=10, pady=(0, 8))

        # Contenu onglet TXT
        self._txt_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkLabel(self._txt_frame, text="Texte à insérer :", font=("Arial", 11)).pack(anchor="w")
        self._text_input = ctk.CTkTextbox(self._txt_frame, height=80, font=("Arial", 11))
        self._text_input.pack(fill="x", pady=(4, 6))
        ctk.CTkButton(self._txt_frame, text="+ Ajouter le texte à la séquence",
                      fg_color=COLOR_TEXT, hover_color="#5a3a7a",
                      command=self._add_text).pack(fill="x")

    def _on_tab_change(self, value: str) -> None:
        if value == "Commande Revit":
            self._txt_frame.pack_forget()
            self._cmd_frame.pack(fill="both", expand=True, padx=10, pady=(0, 8))
        else:
            self._cmd_frame.pack_forget()
            self._txt_frame.pack(fill="both", expand=True, padx=10, pady=(0, 8))

    # ── Séquence ────────────────────────────────────────────────────────────

    def _refresh_sequence(self) -> None:
        for w in self._seq_frame.winfo_children():
            w.destroy()
        if not self._sequence:
            ctk.CTkLabel(self._seq_frame, text="(aucune action)", text_color="gray",
                         font=("Arial", 10)).pack(pady=6)
            return
        for i, item in enumerate(self._sequence):
            self._add_seq_row(i, item)

    def _add_seq_row(self, i: int, item: SequenceItem) -> None:
        is_key  = item["type"] == "key"
        color   = COLOR_CMD if is_key else COLOR_TEXT
        badge   = "CMD" if is_key else "TXT"
        row = ctk.CTkFrame(self._seq_frame, fg_color="transparent")
        row.pack(fill="x", padx=4, pady=2)
        # Flèches
        ctk.CTkButton(row, text="▲", width=22, height=20, font=("Arial", 8),
                      fg_color="#333", hover_color="#555",
                      command=lambda idx=i: self._move(idx, -1)).pack(side="left", padx=(0, 1))
        ctk.CTkButton(row, text="▼", width=22, height=20, font=("Arial", 8),
                      fg_color="#333", hover_color="#555",
                      command=lambda idx=i: self._move(idx, 1)).pack(side="left", padx=(0, 5))
        # Badge type
        ctk.CTkLabel(row, text=badge, width=34, height=20, font=("Arial", 9, "bold"),
                     text_color="white", fg_color=color, corner_radius=4).pack(side="left", padx=(0, 5))
        # Valeur
        display = item["value"] if len(item["value"]) <= 30 else item["value"][:28] + "…"
        ctk.CTkLabel(row, text=display, font=("Arial", 10), anchor="w").pack(side="left", fill="x", expand=True)
        # Supprimer
        ctk.CTkButton(row, text="✕", width=24, height=20, font=("Arial", 9),
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
        self._sequence.append({"type": "key", "value": code})
        self._refresh_sequence()
        self._emit()

    def _add_text(self) -> None:
        if not self._active_key:
            return
        text = self._text_input.get("1.0", "end").strip()
        if not text:
            return
        self._sequence.append({"type": "text", "value": text})
        self._text_input.delete("1.0", "end")
        self._refresh_sequence()
        self._emit()

    def _emit(self) -> None:
        if self._on_change:
            self._on_change(list(self._sequence))

    # ── Recherche commandes ──────────────────────────────────────────────────

    def _refresh_search(self, query: str) -> None:
        for w in self._list_frame.winfo_children():
            w.destroy()
        for cmd in search(self._all_commands, query):
            self._add_search_row(cmd)

    def _add_search_row(self, cmd: RevitCommand) -> None:
        ctk.CTkButton(
            self._list_frame,
            text=f"{cmd.code}  —  {cmd.name}",
            anchor="w",
            font=("Arial", 11),
            fg_color="transparent",
            hover_color=COLOR_CMD,
            height=28,
            command=lambda c=cmd: self._add_command(c.code),
        ).pack(fill="x", pady=1)

    # ── Interface publique ───────────────────────────────────────────────────

    def set_active_key(self, key: str | None, sequence: list[SequenceItem] | None = None) -> None:
        self._active_key = key
        self._sequence = list(sequence or [])
        if key:
            self._key_label.configure(text=f"Touche : {key}", text_color="white")
        else:
            self._key_label.configure(text="Aucune touche sélectionnée", text_color="gray")
        self._refresh_sequence()
