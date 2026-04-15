import unittest
from unittest.mock import patch, MagicMock

from src.rat.commands.ipconfig import IPConfigCommand


class TestIPConfigCommand(unittest.TestCase):

    @patch("rat.commands.ipconfig.subprocess.run")
    @patch("rat.commands.ipconfig.platform.system")
    def test_windows_ipconfig(self, mock_system, mock_run):

        mock_system.return_value = "Windows"

        mock_run.return_value = MagicMock(
            returncode=0, stdout="Windows IP Configuration", stderr=""
        )

        cmd = IPConfigCommand()

        result = cmd.execute("")

        self.assertIn("Windows IP Configuration", result)

        mock_run.assert_called_with(
            ["ipconfig"],
            capture_output=True,
            text=True,
        )

    @patch("rat.commands.ipconfig.subprocess.run")
    @patch("rat.commands.ipconfig.platform.system")
    def test_linux_ipconfig(self, mock_system, mock_run):

        mock_system.return_value = "Linux"

        mock_run.return_value = MagicMock(
            returncode=0, stdout="inet 192.168.1.10", stderr=""
        )

        cmd = IPConfigCommand()

        result = cmd.execute("")

        self.assertIn("inet", result)

        mock_run.assert_called_with(
            ["ip", "addr"],
            capture_output=True,
            text=True,
        )

    @patch("rat.commands.ipconfig.platform.system")
    def test_unsupported_os(self, mock_system):

        mock_system.return_value = "Solaris"

        cmd = IPConfigCommand()

        result = cmd.execute("")

        self.assertEqual(result, "Unsupported OS: Solaris")
