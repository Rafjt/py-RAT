# Ce module fournit un service simple pour capturer un screenshot de l’écran.
# Il utilise la bibliothèque mss pour une capture rapide et multiplateforme,
# puis convertit l’image en PNG directement en mémoire (bytes),

import mss
import mss.tools


class ScreenshotService:

    def capture(self) -> bytes:

        # Initialise le gestionnaire de capture d’écran
        with mss.mss() as sct:

            # Sélectionne le moniteur principal (index 1)
            # (index 0 = tous les écrans combinés)
            monitor = sct.monitors[1]

            # Capture brute de l’écran
            screenshot = sct.grab(monitor)

            # Conversion en PNG depuis les données RGB
            return mss.tools.to_png(screenshot.rgb, screenshot.size)
