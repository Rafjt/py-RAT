import unittest
from unittest.mock import patch

from rat.commands.download import DownloadCommand


class TestDownloadCommand(unittest.TestCase):

    def setUp(self):

        self.cmd = DownloadCommand()

    # SUCCESS
    @patch("rat.commands.download.Path.read_bytes")
    @patch("rat.commands.download.Path.is_file")
    @patch("rat.commands.download.Path.exists")
    def test_download_success(
        self,
        mock_exists,
        mock_is_file,
        mock_read_bytes,
    ):

        mock_exists.return_value = True
        mock_is_file.return_value = True
        mock_read_bytes.return_value = b"hello world"

        result = self.cmd.execute("/tmp/test.txt")

        self.assertTrue(result.startswith("DOWNLOAD"))
        self.assertIn("OK", result)
        self.assertIn("hello world", result)
        self.assertTrue(result.endswith("EOF"))

    # FILE NOT FOUND
    @patch("rat.commands.download.Path.exists")
    def test_file_not_found(self, mock_exists):

        mock_exists.return_value = False

        result = self.cmd.execute("/tmp/missing.txt")

        self.assertIn("ERROR", result)
        self.assertIn("File not found", result)

    # NOT A FILE
    @patch("rat.commands.download.Path.is_file")
    @patch("rat.commands.download.Path.exists")
    def test_not_a_file(
        self,
        mock_exists,
        mock_is_file,
    ):

        mock_exists.return_value = True
        mock_is_file.return_value = False

        result = self.cmd.execute("/tmp")

        self.assertIn("ERROR", result)
        self.assertIn("Not a file", result)

    # EMPTY ARG
    def test_empty_argument(self):

        result = self.cmd.execute("")

        self.assertIn("ERROR", result)
        self.assertIn("No file path", result)

    # READ ERROR
    @patch("rat.commands.download.Path.read_bytes")
    @patch("rat.commands.download.Path.is_file")
    @patch("rat.commands.download.Path.exists")
    def test_read_exception(
        self,
        mock_exists,
        mock_is_file,
        mock_read_bytes,
    ):

        mock_exists.return_value = True
        mock_is_file.return_value = True

        mock_read_bytes.side_effect = Exception("disk error")

        result = self.cmd.execute("/tmp/test.txt")

        self.assertIn("ERROR", result)
        self.assertIn("disk error", result)
