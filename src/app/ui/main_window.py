"""
Fenêtre principale de l'application.
"""
from pathlib import Path
import customtkinter as ctk

from app.ui.keyboard_view import KeyboardView
from app.ui.mouse_view import MouseView
from app.ui.command_panel import CommandPanel
from app.ui.log_window import LogWindow
from app.ui.compact_window import CompactWindow
from app.core import ahk_manager, profile_manager
from app.core import logger
from app.config import get_ahk_script_path, set_ahk_script_path


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Revit Macro Tool — Configuration")
        self.geometry("1200x780")
        self.resizable(False, False)
        self._active_key: str | None = None
        self._active_view = None
        self._log_window: LogWindow | None = None
        self._compact: CompactWindow | None = None

        self._profiles: list[dict] = profile_manager.load()
        self._active_profile_idx: int = 0

        self._build_ui()
        logger.info("Application démarrée")
        self._refresh_profile_selector()
        self._load_active_profile()
        self._auto_launch_ahk()

    def _build_ui(self) -> None:
        # Barre du haut — script AHK
        top = ctk.CTkFrame(self, height=44)
        top.pack(fill="x", padx=10, pady=(10, 0))
        top.pack_propagate(False)

        ctk.CTkLabel(top, text="Script AHK :", font=("Arial", 11)).pack(side="left", padx=(8, 4))
        self._script_path_var = ctk.StringVar(value=str(get_ahk_script_path()))
        ctk.CTkEntry(top, textvariable=self._script_path_var, width=480, font=("Arial", 10)).pack(side="left")
        ctk.CTkButton(top, text="Parcourir", width=80, height=28,
                      command=self._browse_script).pack(side="left", padx=4)
        ctk.CTkButton(top, text="▶ Lancer AHK", width=110, height=28,
                      fg_color="#2d6e3e", hover_color="#1f5530",
                      command=self._launch_ahk).pack(side="left", padx=2)
        ctk.CTkButton(top, text="⧉ Vue compacte", width=110, height=28,
                      fg_color="#4a4a4a", hover_color="#555",
                      command=self._show_compact).pack(side="left", padx=8)
        ctk.CTkButton(top, text="📋 Logs", width=75, height=28,
                      fg_color="#333", hover_color="#444",
                      command=self._open_logs).pack(side="right", padx=8)

        # Barre profils
        prof_bar = ctk.CTkFrame(self, height=44)
        prof_bar.pack(fill="x", padx=10, pady=(6, 0))
        prof_bar.pack_propagate(False)

        ctk.CTkLabel(prof_bar, text="Profil :", font=("Arial", 11)).pack(side="left", padx=(8, 4))
        self._profile_var = ctk.StringVar()
        self._profile_combo = ctk.CTkOptionMenu(
            prof_bar, variable=self._profile_var, width=200,
            command=self._on_profile_selected, values=[],
        )
        self._profile_combo.pack(side="left", padx=4)
        ctk.CTkButton(prof_bar, text="+ Nouveau", width=90, height=28,
                      command=self._add_profile).pack(side="left", padx=4)
        ctk.CTkButton(prof_bar, text="✎ Renommer", width=100, height=28,
                      command=self._rename_profile).pack(side="left", padx=2)
        ctk.CTkButton(prof_bar, text="🗑 Supprimer", width=100, height=28,
                      fg_color="#6e2d2d", hover_color="#552222",
                      command=self._delete_profile).pack(side="left", padx=2)

        # Panneau gauche — clavier + souris
        left = ctk.CTkFrame(self)
        left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self._keyboard = KeyboardView(left, on_select=self._on_key_selected)
        self._keyboard.pack(fill="both", expand=True)

        self._mouse = MouseView(left, on_select=self._on_key_selected)
        self._mouse.pack(fill="x", pady=(8, 0))

        # Panneau droit — gestion des séquences
        right = ctk.CTkFrame(self, width=340)
        right.pack(side="right", fill="y", padx=(0, 10), pady=10)
        right.pack_propagate(False)

        self._panel = CommandPanel(right, on_change=self._on_sequence_change)
        self._panel.pack(fill="both", expand=True)

    # ── Profils ──────────────────────────────────────────────────────────────

    def _active_profile(self) -> dict | None:
        if 0 <= self._active_profile_idx < len(self._profiles):
            return self._profiles[self._active_profile_idx]
        return None

    def _refresh_profile_selector(self) -> None:
        names = [p["name"] for p in self._profiles]
        self._profile_combo.configure(values=names if names else [""])
        if self._profiles:
            self._profile_var.set(self._profiles[self._active_profile_idx]["name"])

    def _clear_views(self) -> None:
        for key in list(self._keyboard.get_assignments().keys()):
            self._keyboard.set_commands(key, [])
        for key in list(self._mouse.get_assignments().keys()):
            self._mouse.set_commands(key, [])

    def _load_active_profile(self) -> None:
        self._clear_views()
        self._active_key = None
        self._active_view = None
        self._panel.set_active_key("", [])

        profile = self._active_profile()
        if profile:
            assignments = profile.get("assignments", {})
            self._keyboard.load_assignments(assignments)
            self._mouse.load_assignments(assignments)
            logger.info(f"Profil chargé : {profile['name']}")

    def _on_profile_selected(self, name: str) -> None:
        for i, p in enumerate(self._profiles):
            if p["name"] == name:
                self._active_profile_idx = i
                break
        self._load_active_profile()

    def _add_profile(self) -> None:
        dialog = ctk.CTkInputDialog(text="Nom du nouveau profil :", title="Nouveau profil")
        name = dialog.get_input()
        if not name or not name.strip():
            return
        profile = profile_manager.new_profile(name.strip())
        self._profiles.append(profile)
        self._active_profile_idx = len(self._profiles) - 1
        self._refresh_profile_selector()
        self._load_active_profile()
        self._save_and_reload()
        logger.success(f"Profil créé : {name.strip()}")

    def _rename_profile(self) -> None:
        profile = self._active_profile()
        if not profile:
            return
        dialog = ctk.CTkInputDialog(text="Nouveau nom :", title="Renommer le profil")
        name = dialog.get_input()
        if not name or not name.strip():
            return
        profile["name"] = name.strip()
        self._refresh_profile_selector()
        self._save_and_reload()
        logger.success(f"Profil renommé : {name.strip()}")

    def _delete_profile(self) -> None:
        if len(self._profiles) <= 1:
            logger.warning("Impossible de supprimer le dernier profil")
            return
        profile = self._active_profile()
        if not profile:
            return
        deleted_name = profile["name"]
        self._profiles.pop(self._active_profile_idx)
        self._active_profile_idx = max(0, self._active_profile_idx - 1)
        self._refresh_profile_selector()
        self._load_active_profile()
        self._save_and_reload()
        logger.success(f"Profil supprimé : {deleted_name}")

    # ── Sélection + séquence ─────────────────────────────────────────────────

    def _on_key_selected(self, key: str) -> None:
        self._active_key = key
        self._active_view = self._keyboard if key in self._keyboard._buttons else self._mouse
        current = self._active_view.get_commands(key)
        self._panel.set_active_key(key, current)
        logger.info(f"Touche sélectionnée : {key} ({len(current)} action(s))")

    def _on_sequence_change(self, sequence: list) -> None:
        if not self._active_key or not self._active_view:
            return
        self._active_view.set_commands(self._active_key, sequence)

        profile = self._active_profile()
        if profile is not None:
            profile["assignments"] = self._get_all_assignments()

        if sequence:
            summary = " + ".join(
                i["value"] if i["type"] == "key" else f'"{i["value"][:15]}"'
                for i in sequence
            )
            logger.success(f"{self._active_key} → {summary}")
        else:
            logger.info(f"Séquence effacée : {self._active_key}")
        self._save_and_reload()

    # ── Sauvegarde + rechargement AHK ────────────────────────────────────────

    def _get_all_assignments(self) -> dict:
        return {**self._keyboard.get_assignments(), **self._mouse.get_assignments()}

    def _save_and_reload(self) -> None:
        script_path = self._get_script_path()
        if not script_path:
            return
        try:
            profile_manager.save(self._profiles)
            ahk_manager.write_profiles(script_path, self._profiles)
            ahk_manager.reload_script(script_path)
            if self._compact and self._compact.winfo_exists():
                self._compact.update_profiles(self._profiles)
        except Exception as e:
            logger.error("Échec mise à jour du script AHK", e)

    def _auto_launch_ahk(self) -> None:
        script_path = self._get_script_path()
        if script_path:
            ahk_manager.launch_script(script_path)

    # ── Navigation + utilitaires ─────────────────────────────────────────────

    def _get_script_path(self) -> Path | None:
        path_str = self._script_path_var.get().strip()
        if not path_str:
            return None
        path = Path(path_str)
        set_ahk_script_path(path)
        return path

    def _browse_script(self) -> None:
        from tkinter import filedialog
        path = filedialog.askopenfilename(
            title="Sélectionner le script AHK",
            filetypes=[("AutoHotkey", "*.ahk"), ("Tous les fichiers", "*.*")],
        )
        if path:
            self._script_path_var.set(path)
            logger.info(f"Script sélectionné : {path}")

    def _launch_ahk(self) -> None:
        script_path = self._get_script_path()
        if script_path:
            ahk_manager.launch_script(script_path)

    def _show_compact(self) -> None:
        script_path = self._get_script_path()
        if not script_path:
            logger.warning("Aucun script AHK configuré")
            return
        if self._compact is None or not self._compact.winfo_exists():
            self._compact = CompactWindow(self, script_path, on_configure=self.deiconify)
        self._compact.update_profiles(self._profiles)
        self._compact.deiconify()
        self.withdraw()

    def _open_logs(self) -> None:
        if self._log_window is None or not self._log_window.winfo_exists():
            self._log_window = LogWindow(self)
        else:
            self._log_window.focus()
