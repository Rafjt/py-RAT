import socket
import ssl
from utils.logger import setup_logger
from commands.command_registry import CommandRegistry

# import subprocess

logger = setup_logger()


class SSLClient:
    def __init__(
        self,
        server_host,
        server_port,
        sni_hostname,
        client_cert,
        client_key,
    ):
        self.server_host = server_host
        self.server_port = server_port
        self.sni_hostname = sni_hostname
        self._context = ssl.SSLContext()
        self._context.load_cert_chain(client_cert, client_key)
        self._sock = None
        self._ssock = None
        self.registry = CommandRegistry()

    def close(self):
        if self._ssock:
            self._ssock.close()
        if self._sock:
            self._sock.close()

    def connect(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._ssock = self._context.wrap_socket(
            self._sock,
        )
        self._ssock.connect((self.server_host, self.server_port))

    def send(self, msg):
        EOM = "__END__"

        self._ssock.sendall((msg + "\n" + EOM + "\n").encode())

    def receive(self):
        try:
            data = self._ssock.recv(4096)

            if not data:
                return None

            return data.decode()

        except Exception as e:
            print(f"Receive error: {e}")
            return None

    def execute_command(self, command: str) -> str:
        command = command.strip()

        if not command:
            return "Empty command"

        parts = command.split(" ", 1)
        cmd_name = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        handler = self.registry.get(cmd_name)

        if handler:
            return handler.execute(args)
        else:
            return "Command not implemented"
