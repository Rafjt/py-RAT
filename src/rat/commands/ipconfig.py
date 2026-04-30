# Ce module implémente une commande de récupération de configuration réseau.
# Elle exécute la commande système appropriée selon l’OS :
# - Windows : ipconfig
# - Linux : ip addr
# - macOS : ifconfig
# et retourne la sortie brute au client.

import platform
import subprocess
from .base_command import BaseCommand


class IPConfigCommand(BaseCommand):

    name = "ipconfig"
    description = "Get the client's network configuration"

    def execute(self, args: str) -> str:

        # Détection du système d’exploitation
        system = platform.system()

        try:

            # Choix de la commande adaptée à l’OS
            if system == "Windows":
                cmd = ["ipconfig"]

            elif system == "Linux":
                cmd = ["ip", "addr"]

            elif system == "Darwin":
                cmd = ["ifconfig"]

            else:
                return f"Unsupported OS: {system}"

            # Exécution de la commande système
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )

            # Gestion des erreurs d’exécution
            if result.returncode != 0:
                return result.stderr

            # Retour de la sortie standard
            return result.stdout

        except Exception as e:
            return f"ipconfig error: {e}"
