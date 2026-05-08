# Revit Macro Tool

Outil de raccourcis et macros pour Revit — L2C Experts.

## Fonctionnalités

- Interface visuelle clavier + souris pour assigner des commandes Revit
- Liste de commandes Revit (CP, DP, EH, HH, VV, etc.)
- Statistiques d'utilisation mensuelles par utilisateur
- Synchronisation vers partage réseau
- Page HTML d'installation

## Structure

```
revit-macro-tool/
├── src/          # Code source principal
├── data/         # Liste de commandes Revit, config
├── install/      # Page HTML d'installation
└── logs/         # Logs locaux (non versionnés)
```

## Développement

Pour tester localement, tous les chemins réseau pointent vers des dossiers locaux configurables.
