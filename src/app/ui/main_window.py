"""
Fenêtre principale de l'application.
"""
import json
from pathlib import Path
import customtkinter as ctk

from app.ui.keyboard_view import KeyboardView
from app.ui.mouse_view import MouseView
from app.ui.command_panel import CommandPanel
from app.ui.log_window import LogWindow
from app.core import ahk_generator
from app.core import logger


ASSIGNMENTS_PATH = Path(__file__).parent.parent.parent.parent / "data_local" / "assignments.json"


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Revit Macro Tool")
        self.geometry("1200x680")
        self.resizable(False, False)
        self._active_key: str | None = None
        self._active_view = None
        self._log_window: LogWindow | None = None
        self._build_ui()
        logger.info("Application démarrée")
        self._load_assignments()

    def _build_ui(self) -> None:
        # Panneau gauche — clavier + souris
        left = ctk.CTkFrame(self)
        left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self._keyboard = KeyboardView(left, on_select=self._on_key_selected)
        self._keyboard.pack(fill="both", expand=True)

        self._mouse = MouseView(left, on_select=self._on_key_selected)
        self._mouse.pack(fill="x", pady=(8, 0))

        # Boutons du bas
        btn_row = ctk.CTkFrame(left, fg_color="transparent")
        btn_row.pack(fill="x", pady=10)

        ctk.CTkButton(
            btn_row,
            text="Générer script AHK",
            height=40,
            font=("Arial", 13, "bold"),
            fg_color="#1f6aa5",
            hover_color="#1a5a8a",
            command=self._generate_ahk,
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))

        ctk.CTkButton(
            btn_row,
            text="📋 Logs",
            height=40,
            width=90,
            font=("Arial", 12),
            fg_color="#333",
            hover_color="#444",
            command=self._open_logs,
        ).pack(side="right")

        # Panneau droit — commandes
        right = ctk.CTkFrame(self, width=320)
        right.pack(side="right", fill="y", padx=(0, 10), pady=10)
        right.pack_propagate(False)

        self._panel = CommandPanel(right, on_assign=self._on_assign)
        self._panel.pack(fill="both", expand=True)

    def _on_key_selected(self, key: str) -> None:
        self._active_key = key
        self._active_view = self._keyboard if key in self._keyboard._buttons else self._mouse
        self._panel.set_active_key(key)
        logger.info(f"Touche sélectionnée : {key}")

    def _on_assign(self, command_code: str) -> None:
        if not self._active_key or not self._active_view:
            return
        if command_code:
            self._active_view.assign(self._active_key, command_code)
            logger.success(f"Assigné : {self._active_key} → {command_code}")
        else:
            self._active_view.unassign(self._active_key)
            logger.info(f"Assignation retirée : {self._active_key}")
        self._save_assignments()

    def _get_all_assignments(self) -> dict[str, str]:
        return {**self._keyboard.get_assignments(), **self._mouse.get_assignments()}

    def _save_assignments(self) -> None:
        try:
            ASSIGNMENTS_PATH.parent.mkdir(exist_ok=True)
            ASSIGNMENTS_PATH.write_text(
                json.dumps(self._get_all_assignments(), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            logger.info(f"Assignations sauvegardées ({len(self._get_all_assignments())} entrées)")
        except Exception as e:
            logger.error("Échec sauvegarde des assignations", e)

    def _load_assignments(self) -> None:
        if not ASSIGNMENTS_PATH.exists():
            logger.info("Aucun fichier d'assignations existant — démarrage à zéro")
            return
        try:
            with open(ASSIGNMENTS_PATH, encoding="utf-8") as f:
                data: dict = json.load(f)
            self._keyboard.load_assignments(data)
            self._mouse.load_assignments(data)
            logger.success(f"Assignations chargées : {len(data)} entrées")
        except Exception as e:
            logger.error("Échec chargement des assignations", e)

    def _generate_ahk(self) -> None:
        assignments = self._get_all_assignments()
        if not assignments:
            logger.warning("Génération AHK annulée — aucune assignation")
            self._show_message("Aucune assignation à générer.", error=True)
            return
        try:
            output = ASSIGNMENTS_PATH.parent / "RevitMacros.ahk"
            ahk_generator.generate(assignments, output)
            logger.success(f"Script AHK généré : {output}")
            self._show_message(f"Script généré :\n{output}")
        except Exception as e:
            logger.error("Échec génération du script AHK", e)
            self._show_message("Erreur lors de la génération du script.", error=True)

    def _open_logs(self) -> None:
        if self._log_window is None or not self._log_window.winfo_exists():
            self._log_window = LogWindow(self)
        else:
            self._log_window.focus()

    def _show_message(self, text: str, error: bool = False) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("Revit Macro Tool")
        dialog.geometry("420x160")
        dialog.grab_set()
        color = "#8b3b3b" if error else "#2d6e3e"
        ctk.CTkLabel(dialog, text=text, wraplength=380, font=("Arial", 12)).pack(expand=True, pady=20)
        ctk.CTkButton(dialog, text="OK", fg_color=color, command=dialog.destroy).pack(pady=(0, 15))
