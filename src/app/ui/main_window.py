"""
Fenêtre principale de l'application.
"""
import customtkinter as ctk
from app.ui.keyboard_view import KeyboardView
from app.ui.mouse_view import MouseView


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Revit Macro Tool")
        self.geometry("1100x700")
        self.resizable(False, False)
        self._build_ui()

    def _build_ui(self) -> None:
        # Panneau gauche — clavier + souris
        left = ctk.CTkFrame(self)
        left.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        KeyboardView(left).pack(fill="both", expand=True)
        MouseView(left).pack(fill="x", pady=(10, 0))

        # Panneau droit — liste de commandes + assignation
        right = ctk.CTkFrame(self, width=300)
        right.pack(side="right", fill="y", padx=(0, 10), pady=10)
        right.pack_propagate(False)

        ctk.CTkLabel(right, text="Commandes Revit", font=("Arial", 14, "bold")).pack(pady=10)
        self._command_list = ctk.CTkScrollableFrame(right)
        self._command_list.pack(fill="both", expand=True, padx=5)

        ctk.CTkButton(right, text="Générer script AHK", command=self._generate_ahk).pack(
            pady=10, padx=10, fill="x"
        )

    def _generate_ahk(self) -> None:
        # TODO: appeler ahk_generator.py avec la config active
        pass
