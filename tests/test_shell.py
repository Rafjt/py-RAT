import unittest
from unittest.mock import patch, MagicMock
import subprocess

from rat.commands.shell import ShellCommand


class TestShellCommand(unittest.TestCase):

    def setUp(self):
        self.cmd = ShellCommand()

    # ------------------------------------------------------------------
    # Empty arguments
    # ------------------------------------------------------------------
    def test_empty_args(self):
        result = self.cmd.execute("")
        self.assertEqual(result, "Usage: shell <command>")

    def test_none_or_whitespace(self):
        result = self.cmd.execute("   ")
        self.assertEqual(result, "Usage: shell <command>")

    # ------------------------------------------------------------------
    # Successful command (stdout only)
    # ------------------------------------------------------------------
    @patch("rat.commands.shell.subprocess.run")
    def test_success_stdout_only(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="file1\nfile2", stderr="")

        result = self.cmd.execute("ls")
        self.assertEqual(result, "file1\nfile2")
        mock_run.assert_called_with(
            "ls", shell=True, capture_output=True, text=True, timeout=30
        )

    # ------------------------------------------------------------------
    # Command with stderr
    # ------------------------------------------------------------------
    @patch("rat.commands.shell.subprocess.run")
    def test_with_stderr(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="out",
            stderr="error message"
        )

        result = self.cmd.execute("badcmd")
        self.assertIn("out", result)
        self.assertIn("error message", result)

    # ------------------------------------------------------------------
    # Command that produces no output
    # ------------------------------------------------------------------
    @patch("rat.commands.shell.subprocess.run")
    def test_no_output(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        result = self.cmd.execute("true")
        self.assertEqual(result, "(no output)")

    # ------------------------------------------------------------------
    # Timeout
    # ------------------------------------------------------------------
    @patch("rat.commands.shell.subprocess.run")
    def test_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="sleep", timeout=30)

        result = self.cmd.execute("sleep 60")
        self.assertEqual(result, "shell error: command timed out (30s)")

    # ------------------------------------------------------------------
    # Generic exception (e.g., permission error)
    # ------------------------------------------------------------------
    @patch("rat.commands.shell.subprocess.run")
    def test_exception(self, mock_run):
        mock_run.side_effect = OSError("Permission denied")

        result = self.cmd.execute("some_command")
        self.assertIn("shell error: Permission denied", result)


if __name__ == "__main__":
    unittest.main()