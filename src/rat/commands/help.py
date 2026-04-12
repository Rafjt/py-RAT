from .base_command import BaseCommand

class HelpCommand(BaseCommand):
    name = "help"

    def execute(self, args: str) -> str:
        return (
            "help: Prints all the possible commands\n"
                "download: Gather files from client and send them to server\n"
                "upload: Gather files from server and send them to client\n"
                "shell: Opens an interactive shell/bash/cmd\n"
                "ipconfig: Get the client's network configuration\n"
                "screenshot: Take a screenshot of the client\n"
                "search: Search for a file on the client's filesystem\n"
                "hashdump: Get the SAM or /etc/shadow file based on the OS\n"
                "keylogger: Log every key of the client\n"
                "webcam_snapshot: Take a picture using the client's webcam\n"
                "webcam_stream: Livestream the client's webcam\n"
                "record_audio: Record the client's audio\n"
        )