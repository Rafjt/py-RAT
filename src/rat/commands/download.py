from .base_command import BaseCommand

class DownloadCommand(BaseCommand):
    name = "download"

    def execute(self, args: str) -> str:
        return "Downloading..."