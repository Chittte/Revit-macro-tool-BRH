# Revit Macro Tool

Outil de raccourcis et macros pour Revit.

## Fonctionnalités

- Interface visuelle clavier (AZERTY) + souris pour assigner des commandes Revit
- Génération automatique d'un script AHK qui tourne en arrière-plan
- Statistiques d'utilisation mensuelles par utilisateur
- Synchronisation vers partage réseau (avec file d'attente si hors réseau)
- Mise à jour silencieuse au démarrage — aucune réinstallation manuelle

## Stack technique

| Composant | Tech |
|---|---|
| Interface | Python + customtkinter |
| Raccourcis clavier | AutoHotkey v1.1 (généré) |
| Distribution | PyInstaller (.exe standalone) |
| Stockage | JSON (local + réseau UNC) |

## Structure

```
revit-macro-tool/
├── src/
│   ├── launcher/         # Vérifie les mises à jour et lance l'app
│   ├── app/
│   │   ├── ui/           # Interface principale (clavier, souris)
│   │   ├── core/         # Génération AHK, stats, sync réseau
│   │   └── config.py     # Gestion de la configuration locale
│   └── viewer/           # App légère de visualisation des stats
├── data/
│   └── revit_commands.json   # Liste des commandes Revit disponibles
├── install/
│   └── README.txt            # Instructions d'installation (copier-coller)
├── config.example.json       # Exemple de configuration
└── requirements.txt
```

## Installation (utilisateur)

1. Copier `launcher.exe` depuis le partage réseau vers son Bureau
2. Double-cliquer pour lancer — les mises à jour se font automatiquement

## Développement

```bash
pip install -r requirements.txt
python src/app/main.py
```

## Versions Revit supportées

Revit 2024, 2025, 2026.
