import base64
from pathlib import Path

def _build_upload_payload(command: str) -> str:
    print(f"[DEBUG] _build_upload_payload received: {command}")
    try:
        parts = command.strip().split(" ", 2)
        if len(parts) != 3:
            return "ERROR: Invalid number of arguments"

        _, src, dst = parts
        path = Path(src)
        print(f"[DEBUG] Looking for file: {path.absolute()}")

        if not path.exists():
            return f"ERROR: File not found: {src}"

        data = path.read_bytes()
        encoded = base64.b64encode(data).decode()
        payload = f"upload {dst}\n{encoded}\nEOF"
        print(f"[DEBUG] Payload length: {len(payload)} bytes")
        return payload
    except Exception as e:
        return f"ERROR: {e}"