"""
Fenêtre compacte flottante — style v1 MacroProfils.
Lit _rmt_profile.txt pour afficher le profil actif en temps réel.
"""
from __future__ import annotations
from pathlib import Path
from typing import Callable
import customtkinter as ctk
from app.core import ahk_manager


class CompactWindow(ctk.CTkToplevel):
    def __init__(self, parent, script_path: Path,
                 on_configure: Callable | None = None) -> None:
        super().__init__(parent)
        self._script_path   = script_path
        self._on_configure  = on_configure
        self._profiles: list[dict] = []
        self._active_idx    = 1   # 1-based, suit AHK
        self._drag_x = self._drag_y = 0
        self._poll_id = None

        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color="#1E1E1E")
        self.geometry("220x60+20+20")

        self._build()
        self._bind_drag(self)

    # ── Construction ─────────────────────────────────────────────────────────

    def _build(self) -> None:
        # Barre titre
        bar = ctk.CTkFrame(self, fg_color="#252526", height=26, corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        self._bind_drag(bar)
        ctk.CTkLabel(bar, text="REVIT MACRO TOOL",
                     font=("Segoe UI", 8, "bold"), text_color="#888").pack(side="left", padx=8)
        ctk.CTkButton(bar, text="x", width=22, height=22,
                      font=("Segoe UI", 9, "bold"), fg_color="transparent",
                      hover_color="#c0392b", text_color="#FF6B6B",
                      command=self.withdraw).pack(side="right", padx=2, pady=2)

        # Liste profils
        self._profiles_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._profiles_frame.pack(fill="x", padx=6, pady=(4, 2))

        # Bas : navigation + configurer
        bottom = ctk.CTkFrame(self, fg_color="#252526", height=26, corner_radius=0)
        bottom.pack(fill="x", side="bottom")
        bottom.pack_propagate(False)
        ctk.CTkButton(bottom, text="▲", width=28, height=22,
                      font=("Segoe UI", 10), fg_color="transparent",
                      hover_color="#3a3a3a", command=self._prev_profile).pack(side="left", padx=2, pady=2)
        ctk.CTkButton(bottom, text="▼", width=28, height=22,
                      font=("Segoe UI", 10), fg_color="transparent",
                      hover_color="#3a3a3a", command=self._next_profile).pack(side="left")
        ctk.CTkButton(bottom, text="⚙ Configurer", height=22,
                      font=("Segoe UI", 9), fg_color="transparent",
                      hover_color="#3a3a3a", text_color="#4FC3F7",
                      command=self._open_config).pack(side="right", padx=4)

    # ── Navigation ───────────────────────────────────────────────────────────

    def _prev_profile(self) -> None:
        if not self._profiles:
            return
        self._active_idx = self._active_idx - 1 if self._active_idx > 1 else len(self._profiles)
        self._refresh()

    def _next_profile(self) -> None:
        if not self._profiles:
            return
        self._active_idx = self._active_idx + 1 if self._active_idx < len(self._profiles) else 1
        self._refresh()

    # ── Données ──────────────────────────────────────────────────────────────

    def update_profiles(self, profiles: list[dict]) -> None:
        self._profiles = profiles
        self._refresh()
        self._start_polling()

    def _start_polling(self) -> None:
        if self._poll_id:
            self.after_cancel(self._poll_id)
        self._poll()

    def _poll(self) -> None:
        """Lit _rmt_profile.txt toutes les 500ms pour suivre AHK."""
        if not self.winfo_exists():
            return
        try:
            idx = ahk_manager.read_active_profile_index(self._script_path)
            if idx != self._active_idx and 1 <= idx <= len(self._profiles):
                self._active_idx = idx
                self._refresh()
        except Exception:
            pass
        self._poll_id = self.after(500, self._poll)

    # ── Affichage ─────────────────────────────────────────────────────────────

    def _refresh(self) -> None:
        for w in self._profiles_frame.winfo_children():
            w.destroy()

        for i, profile in enumerate(self._profiles, start=1):
            is_active = (i == self._active_idx)
            row = ctk.CTkFrame(self._profiles_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)

            # Indicateur actif
            indicator = "  ►  " if is_active else "      "
            name_color = "#4FC3F7" if is_active else "#555555"
            font_weight = "bold" if is_active else "normal"

            name_btn = ctk.CTkButton(
                row,
                text=f"{indicator}{profile['name']}",
                anchor="w",
                font=("Segoe UI", 10, font_weight),
                text_color=name_color,
                fg_color="transparent",
                hover_color="#2a2a2a",
                height=22,
                command=lambda idx=i: self._select_profile(idx),
            )
            name_btn.pack(side="left", fill="x", expand=True)

            # Résumé des assignations du profil
            summary = _profile_summary(profile)
            if summary:
                ctk.CTkLabel(row, text=summary, font=("Segoe UI", 8),
                             text_color="#666", anchor="e").pack(side="right", padx=4)

        height = 26 + max(len(self._profiles), 1) * 26 + 26 + 8
        x, y = self.winfo_x(), self.winfo_y()
        self.geometry(f"220x{height}+{x}+{y}")

    def _select_profile(self, idx: int) -> None:
        self._active_idx = idx
        self._refresh()

    # ── Drag ─────────────────────────────────────────────────────────────────

    def _bind_drag(self, widget) -> None:
        widget.bind("<ButtonPress-1>", self._start_drag)
        widget.bind("<B1-Motion>",     self._do_drag)

    def _start_drag(self, event) -> None:
        self._drag_x = event.x_root - self.winfo_x()
        self._drag_y = event.y_root - self.winfo_y()

    def _do_drag(self, event) -> None:
        self.geometry(f"+{event.x_root - self._drag_x}+{event.y_root - self._drag_y}")

    def _open_config(self) -> None:
        if self._on_configure:
            self._on_configure()


def _profile_summary(profile: dict) -> str:
    assignments = profile.get("assignments", {})
    assigned = [k for k, v in assignments.items() if v]
    if not assigned:
        return ""
    parts = []
    for key in assigned[:3]:
        seq = assignments[key]
        first = seq[0]["value"] if seq and seq[0]["type"] == "key" else "TXT"
        parts.append(f"{key}:{first}")
    suffix = "…" if len(assigned) > 3 else ""
    return "  ".join(parts) + suffix
