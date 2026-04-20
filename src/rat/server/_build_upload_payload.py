import base64
from pathlib import Path

def _build_upload_payload(command: str) -> str:
    try:
        parts = command.strip().split(" ", 2)
        if len(parts) != 3:

        _, src, dst = parts
        path = Path(src)

        if not path.exists():
            return f"ERROR: File not found: {src}"

        data = path.read_bytes()
        encoded = base64.b64encode(data).decode()
    except Exception as e:
        return f"ERROR: {e}"