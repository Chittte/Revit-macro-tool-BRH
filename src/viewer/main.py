"""
Visionneuse de statistiques — application légère séparée.
Lit les fichiers JSON du partage réseau et affiche les stats par utilisateur/mois.
"""
import json
from pathlib import Path

import customtkinter as ctk


class ViewerWindow(ctk.CTk):
    def __init__(self, network_path: str) -> None:
        super().__init__()
        self.title("Revit Macro Tool — Stats")
        self.geometry("700x500")
        self._network_path = Path(network_path) / "stats"
        self._build_ui()
        self._load_stats()

    def _build_ui(self) -> None:
        ctk.CTkLabel(self, text="Statistiques d'utilisation", font=("Arial", 16, "bold")).pack(pady=15)
        self._table = ctk.CTkScrollableFrame(self)
        self._table.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def _load_stats(self) -> None:
        if not self._network_path.exists():
            ctk.CTkLabel(self._table, text="Partage réseau inaccessible.").pack()
            return
        for stat_file in sorted(self._network_path.glob("*.json")):
            user_id = stat_file.stem
            with open(stat_file, encoding="utf-8") as f:
                data: dict = json.load(f)
            row = ctk.CTkFrame(self._table, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=user_id, width=250, anchor="w").pack(side="left")
            for month, count in sorted(data.items()):
                ctk.CTkLabel(row, text=f"{month}: {count}", width=120).pack(side="left", padx=5)


def main() -> None:
    import sys
    network_path = sys.argv[1] if len(sys.argv) > 1 else ""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = ViewerWindow(network_path)
    app.mainloop()


if __name__ == "__main__":
    main()
