from pathlib import Path
import base64
from .base_command import BaseCommand


class UploadCommand(BaseCommand):
    name = "upload"
    description = "Receive file from server and save it"

    def execute(self, args: str) -> str:
        try:
            if "\n" not in args:
                return "UPLOAD\nERROR\nInvalid format (missing newline)\nEOF"

            dst_path_str, encoded = args.split("\n", 1)
            dst_path = Path(dst_path_str.strip())
            encoded = encoded.strip()

            # 🔧 Auto‑repair missing base64 padding
            missing = len(encoded) % 4
            if missing:
                encoded += "=" * (4 - missing)

            # Handle empty file (empty string becomes b"")
            data = base64.b64decode(encoded) if encoded else b""

            dst_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dst_path, "wb") as f:
                f.write(data)

            return "UPLOAD\nOK\nEOF"
        except Exception as e:
            return f"UPLOAD\nERROR\n{e}\nEOF"
