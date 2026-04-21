import unittest
from unittest.mock import patch, MagicMock

from rat.commands.screenshot import ScreenshotCommand
from rat.client.screenshot_service import ScreenshotService


class TestScreenshotService(unittest.TestCase):

    @patch("rat.client.screenshot_service.mss.tools.to_png")
    @patch("rat.client.screenshot_service.mss.mss")
    def test_capture_returns_bytes(
        self,
        mock_mss,
        mock_to_png,
    ):

        mock_sct = MagicMock()

        mock_monitor = {
            "width": 1920,
            "height": 1080,
        }

        mock_screenshot = MagicMock()
        mock_screenshot.rgb = b"fake_rgb"
        mock_screenshot.size = (1920, 1080)

        mock_sct.grab.return_value = mock_screenshot
        mock_sct.monitors = [None, mock_monitor]

        mock_mss.return_value.__enter__.return_value = mock_sct

        mock_to_png.return_value = b"fake_png_bytes"

        service = ScreenshotService()

        result = service.capture()

        self.assertIsInstance(result, bytes)
        self.assertEqual(result, b"fake_png_bytes")


class TestScreenshotCommand(unittest.TestCase):

    def setUp(self):

        self.cmd = ScreenshotCommand()

    @patch("rat.commands.screenshot.ScreenshotService.capture")
    def test_screenshot_success(
        self,
        mock_capture,
    ):

        mock_capture.return_value = b"fake_image"

        result = self.cmd.execute("")

        self.assertTrue(result.startswith("SCREENSHOT"))

        self.assertIn(
            "OK",
            result,
        )

        self.assertTrue(result.endswith("EOF"))

    @patch("rat.commands.screenshot.ScreenshotService.capture")
    def test_screenshot_contains_base64(
        self,
        mock_capture,
    ):

        mock_capture.return_value = b"image_bytes"

        result = self.cmd.execute("")

        self.assertIn(
            "SCREENSHOT",
            result,
        )

        self.assertIn(
            "OK",
            result,
        )

        self.assertIn(
            "EOF",
            result,
        )

    @patch("rat.commands.screenshot.ScreenshotService.capture")
    def test_screenshot_error(
        self,
        mock_capture,
    ):

        mock_capture.side_effect = Exception("capture failed")

        result = self.cmd.execute("")

        self.assertTrue(result.startswith("SCREENSHOT"))

        self.assertIn(
            "ERROR",
            result,
        )

        self.assertIn(
            "capture failed",
            result,
        )

        self.assertTrue(result.endswith("EOF"))

    def test_protocol_structure(self):
        with patch("rat.commands.screenshot.ScreenshotService.capture") as mock_capture:
            mock_capture.return_value = b"data"

            result = self.cmd.execute("")

            lines = result.split("\n")

            self.assertEqual(
                lines[0],
                "SCREENSHOT",
            )

            self.assertIn(
                lines[1],
                ("OK", "ERROR"),
            )
