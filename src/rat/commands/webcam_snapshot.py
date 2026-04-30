# Commande permettant de capturer une image unique depuis la webcam.
# Elle ouvre la caméra, capture une frame, puis la renvoie encodée en base64.

import cv2
import base64


class WebcamSnapshotCommand:

    # Nom utilisé par le registry pour exécuter la commande
    name = "webcam_snapshot"

    def execute(self, args: str) -> str:

        try:

            # Ouverture de la webcam (device 0 par défaut)
            cap = cv2.VideoCapture(0)

            # Vérifie que la caméra est accessible
            if not cap.isOpened():
                return "WEBCAM\nERROR\nCamera not available"

            # Capture d'une image unique
            ret, frame = cap.read()

            # Libération immédiate de la caméra
            cap.release()

            # Vérifie que la capture a réussi
            if not ret:
                return "WEBCAM\nERROR\nFailed to capture frame"

            # Encodage de l'image en JPEG
            success, buffer = cv2.imencode(".jpg", frame)

            if not success:
                return "WEBCAM\nERROR\nEncoding failed"

            # Conversion en base64 pour transmission texte
            encoded = base64.b64encode(buffer).decode()

            # Retour structuré de l’image capturée
            return "WEBCAM\n" "OK\n" + encoded

        except Exception as e:

            # Gestion globale des erreurs caméra / encodage
            return "WEBCAM\n" "ERROR\n" + str(e)
