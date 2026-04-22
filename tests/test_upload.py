import unittest
from unittest.mock import patch, mock_open
import base64
from pathlib import Path

from rat.commands.upload import UploadCommand


class TestUploadCommand(unittest.TestCase):

    def setUp(self):
        self.cmd = UploadCommand()

    # SUCCESS (non-empty file)
    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_upload_success(self, mock_mkdir, mock_file):
        """Upload a normal file with base64 content."""
        content = b"hello world"
        encoded = base64.b64encode(content).decode()
        args = f"remote.txt\n{encoded}"

        result = self.cmd.execute(args)

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_file.assert_called_once_with(Path("remote.txt"), "wb")
        mock_file().write.assert_called_once_with(content)

        self.assertEqual(result, "UPLOAD\nOK\nEOF")

    # SUCCESS (empty file)
    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_upload_empty_file(self, mock_mkdir, mock_file):
        """Upload an empty file (encoded empty string)."""
        args = "empty.txt\n"   # encoded part is empty after the newline

        result = self.cmd.execute(args)

        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_file.assert_called_once_with(Path("empty.txt"), "wb")
        mock_file().write.assert_called_once_with(b"")

        self.assertEqual(result, "UPLOAD\nOK\nEOF")

    # INVALID FORMAT - missing newline
    def test_missing_newline(self):
        """Command argument does not contain a newline separator."""
        args = "only_filename"

        result = self.cmd.execute(args)

        self.assertIn("ERROR", result)
        self.assertIn("missing newline", result)

    # INVALID BASE64
    @patch("builtins.open", new_callable=mock_open)
    @patch("pathlib.Path.mkdir")
    def test_invalid_base64(self, mock_mkdir, mock_file):
        """Encoded part is not valid base64."""
        args = "remote.txt\n!!!not-base64!!!"

        result = self.cmd.execute(args)

        # mkdir should NOT be called because base64 decoding fails first
        mock_mkdir.assert_not_called()
        mock_file.assert_not_called()

        self.assertIn("ERROR", result)
        # The exact error message may contain 'binascii' or 'Invalid base64'
        # We just check that an error was returned.
        self.assertNotIn("OK", result)

    # FILESYSTEM WRITE ERROR
    @patch("builtins.open", side_effect=PermissionError("Permission denied"))
    @patch("pathlib.Path.mkdir")
    def test_write_permission_error(self, mock_mkdir, mock_open):
        """Simulate a permission error when writing the file."""
        content = b"data"
        encoded = base64.b64encode(content).decode()
        args = f"protected.txt\n{encoded}"

        result = self.cmd.execute(args)

        mock_mkdir.assert_called_once()
        mock_open.assert_called_once()

        self.assertIn("ERROR", result)
        self.assertIn("Permission denied", result)

    # DIRECTORY CREATION ERROR
    @patch("pathlib.Path.mkdir", side_effect=OSError("Cannot create directory"))
    def test_mkdir_error(self, mock_mkdir):
        """Simulate an error when creating parent directories."""
        content = b"data"
        encoded = base64.b64encode(content).decode()
        args = f"deep/nested/file.txt\n{encoded}"

        result = self.cmd.execute(args)

        mock_mkdir.assert_called_once()
        self.assertIn("ERROR", result)
        self.assertIn("Cannot create directory", result)


if __name__ == "__main__":
    unittest.main()