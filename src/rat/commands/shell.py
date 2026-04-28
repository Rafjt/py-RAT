import subprocess
from .base_command import BaseCommand


class ShellCommand(BaseCommand):
    name = "shell"
    description = "Execute a shell command and return the output"

    def execute(self, args: str) -> str:
        if not args.strip():
            return "Usage: shell <command>"

        try:
            # shell=True allows built‑ins like dir/cd on Windows, ls/pwd on Linux
            result = subprocess.run(
                args,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,  # prevent hanging forever
            )
            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr
            return output if output else "(no output)"
        except subprocess.TimeoutExpired:
            return "shell error: command timed out (30s)"
        except Exception as e:
            return f"shell error: {e}"
