"""
Launcher — vérifie la version sur le réseau, met à jour si nécessaire, lance l'app.
"""
import json
import subprocess
import sys
from pathlib import Path


APP_NAME = "RevitMacroTool.exe"
VERSION_FILE = "version.json"
CONFIG_FILE = "config.json"


def load_config() -> dict:
    config_path = Path(sys.executable).parent / CONFIG_FILE
    if not config_path.exists():
        config_path = Path(__file__).parent.parent.parent / CONFIG_FILE
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


def get_local_version() -> str:
    version_path = Path(sys.executable).parent / VERSION_FILE
    if not version_path.exists():
        return "0.0.0"
    with open(version_path, encoding="utf-8") as f:
        return json.load(f).get("version", "0.0.0")


def get_remote_version(network_path: str) -> str | None:
    remote_version_path = Path(network_path) / VERSION_FILE
    try:
        with open(remote_version_path, encoding="utf-8") as f:
            return json.load(f).get("version")
    except Exception:
        return None


def update_and_restart(network_path: str) -> None:
    local_dir = Path(sys.executable).parent
    remote_exe = Path(network_path) / APP_NAME
    local_exe = local_dir / APP_NAME
    # Copie via un .bat temporaire pour remplacer le .exe pendant son exécution
    bat = local_dir / "_update.bat"
    bat.write_text(
        f'@echo off\n'
        f'timeout /t 1 /nobreak >nul\n'
        f'copy /y "{remote_exe}" "{local_exe}"\n'
        f'copy /y "{Path(network_path) / VERSION_FILE}" "{local_dir / VERSION_FILE}"\n'
        f'start "" "{local_exe}"\n'
        f'del "%~f0"\n',
        encoding="utf-8",
    )
    subprocess.Popen(["cmd", "/c", str(bat)], creationflags=subprocess.CREATE_NO_WINDOW)
    sys.exit(0)


def main() -> None:
    try:
        config = load_config()
        network_path = config.get("network_path", "")
    except Exception:
        network_path = ""

    if network_path:
        remote_version = get_remote_version(network_path)
        local_version = get_local_version()
        if remote_version and remote_version != local_version:
            update_and_restart(network_path)

    # Lance l'app principale
    local_dir = Path(sys.executable).parent
    app_exe = local_dir / APP_NAME
    if app_exe.exists():
        subprocess.Popen([str(app_exe)])
    else:
        # Mode développement — lance main.py directement
        app_main = Path(__file__).parent.parent / "app" / "main.py"
        subprocess.Popen([sys.executable, str(app_main)])


if __name__ == "__main__":
    main()
