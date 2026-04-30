# Commande permettant de recevoir un fichier encodé depuis le serveur
# et de l’écrire sur le système de fichiers du client.
# Le contenu est transmis en base64 afin de garantir une transmission sûre.

from pathlib import Path
import base64
from .base_command import BaseCommand


class UploadCommand(BaseCommand):

    # Nom utilisé par le registry pour appeler la commande
    name = "upload"

    description = "Receive file from server and save it"

    def execute(self, args: str) -> str:

        try:

            # Vérifie que le format attendu est respecté :
            # "chemin_destination\ncontenu_base64"
            if "\n" not in args:
                return "UPLOAD\nERROR\nInvalid format (missing newline)\nEOF"

            # Séparation du chemin et des données encodées
            dst_path_str, encoded = args.split("\n", 1)

            # Normalisation du chemin cible
            dst_path = Path(dst_path_str.strip())

            # Nettoyage des données base64
            encoded = encoded.strip()

            # Correction automatique du padding base64 si incomplet
            missing = len(encoded) % 4
            if missing:
                encoded += "=" * (4 - missing)

            # Décodage du contenu (gestion du cas fichier vide)
            data = base64.b64decode(encoded) if encoded else b""

            # Création du dossier cible si nécessaire
            dst_path.parent.mkdir(parents=True, exist_ok=True)

            # Écriture du fichier en mode binaire
            with open(dst_path, "wb") as f:
                f.write(data)

            return "UPLOAD\nOK\nEOF"

        except Exception as e:
            # Retour d’erreur standardisé en cas d’échec
            return f"UPLOAD\nERROR\n{e}\nEOF"
