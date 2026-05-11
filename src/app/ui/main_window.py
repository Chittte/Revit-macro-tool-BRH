"""
Fenêtre principale de l'application.
"""
from pathlib import Path
import customtkinter as ctk

from app.ui.keyboard_view import KeyboardView
from app.ui.mouse_view import MouseView
from app.ui.command_panel import CommandPanel
from app.ui.log_window import LogWindow
from app.core import ahk_manager
from app.core import logger
from app.config import get_ahk_script_path, set_ahk_script_path


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Revit Macro Tool")
        self.geometry("1200x720")
        self.resizable(False, False)
        self._active_key: str | None = None
        self._active_view = None
        self._log_window: LogWindow | None = None
        self._build_ui()
        logger.info("Application démarrée")
        self._load_from_script()

    def _build_ui(self) -> None:
        # Barre du haut — chemin du script AHK
        top = ctk.CTkFrame(self, height=44)
        top.pack(fill="x", padx=10, pady=(10, 0))
        top.pack_propagate(False)

        ctk.CTkLabel(top, text="Script AHK :", font=("Arial", 11)).pack(side="left", padx=(8, 4))
        self._script_path_var = ctk.StringVar(value=str(get_ahk_script_path()))
        ctk.CTkEntry(top, textvariable=self._script_path_var, width=560, font=("Arial", 10)).pack(side="left")
        ctk.CTkButton(top, text="Parcourir", width=80, height=28,
                      command=self._browse_script).pack(side="left", padx=6)
        ctk.CTkButton(top, text="▶ Lancer AHK", width=110, height=28,
                      fg_color="#2d6e3e", hover_color="#1f5530",
                      command=self._launch_ahk).pack(side="left", padx=2)
        ctk.CTkButton(top, text="📋 Logs", width=80, height=28,
                      fg_color="#333", hover_color="#444",
                      command=self._open_logs).pack(side="right", padx=8)

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

    def _on_key_selected(self, key: str) -> None:
        self._active_key = key
        self._active_view = self._keyboard if key in self._keyboard._buttons else self._mouse
        current_commands = self._active_view.get_commands(key)
        self._panel.set_active_key(key, current_commands)
        logger.info(f"Touche sélectionnée : {key} ({len(current_commands)} commande(s))")

    def _on_sequence_change(self, commands: list[str]) -> None:
        if not self._active_key or not self._active_view:
            return
        self._active_view.set_commands(self._active_key, commands)
        if commands:
            logger.success(f"{self._active_key} → {' + '.join(commands)}")
        else:
            logger.info(f"Séquence effacée : {self._active_key}")
        self._save_to_script()

    def _get_all_assignments(self) -> dict[str, list[str]]:
        return {**self._keyboard.get_assignments(), **self._mouse.get_assignments()}

    def _save_to_script(self) -> None:
        script_path = self._get_script_path()
        if not script_path:
            return
        try:
            ahk_manager.write_assignments(script_path, self._get_all_assignments())
            ahk_manager.reload_script(script_path)
        except Exception as e:
            logger.error("Échec mise à jour du script AHK", e)

    def _load_from_script(self) -> None:
        script_path = self._get_script_path()
        if not script_path or not script_path.exists():
            logger.info("Aucun script AHK existant — démarrage à zéro")
            return
        try:
            assignments = ahk_manager.read_assignments(script_path)
            self._keyboard.load_assignments(assignments)
            self._mouse.load_assignments(assignments)
        except Exception as e:
            logger.error("Échec lecture du script AHK", e)

    def _get_script_path(self) -> Path | None:
        path_str = self._script_path_var.get().strip()
        if not path_str:
            logger.warning("Aucun chemin de script AHK configuré")
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
            self._load_from_script()

    def _launch_ahk(self) -> None:
        script_path = self._get_script_path()
        if script_path:
            ahk_manager.launch_script(script_path)

    def _open_logs(self) -> None:
        if self._log_window is None or not self._log_window.winfo_exists():
            self._log_window = LogWindow(self)
        else:
            self._log_window.focus()
