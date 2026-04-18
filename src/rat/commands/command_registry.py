from .help import HelpCommand
from .download import DownloadCommand
from .shell import ShellCommand
from .ipconfig import IPConfigCommand
from .keylogger import KeyloggerCommand


class CommandRegistry:
    def __init__(self):
        self.commands = {}

        self.register(HelpCommand())
        self.register(DownloadCommand())
        self.register(ShellCommand())
        self.register(IPConfigCommand())
        self.register(KeyloggerCommand())

    def register(self, command):
        self.commands[command.name] = command

    def get(self, name):
        return self.commands.get(name)