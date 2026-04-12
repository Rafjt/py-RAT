from .help import HelpCommand
from .download import DownloadCommand

class CommandRegistry:
    def __init__(self):
        self.commands = {}

        self.register(HelpCommand())
        self.register(DownloadCommand())

    def register(self, command):
        self.commands[command.name] = command

    def get(self, name):
        return self.commands.get(name)