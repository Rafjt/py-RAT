import base64
from pathlib import Path

def _build_upload_payload(command: str) -> str:
    try:
        parts = command.strip().split(" ", 2)
        if len(parts) != 3:
            return "ERROR: Usage: upload <src> <dst>"

        _, src, dst = parts
        path = Path(src)

        if not path.exists():
            return f"ERROR: File not found: {src}"
        if path.stat().st_size == 0:
            return "ERROR: File is empty (upload of empty files is disabled)"

        data = path.read_bytes()
        encoded = base64.b64encode(data).decode()
        return f"upload {dst}\n{encoded}\nEOF"
    except Exception as e:
        return f"ERROR: {e}"