import unittest
from unittest.mock import patch, MagicMock, mock_open

from rat.commands.hashdump import HashdumpCommand


class TestHashdumpCommand(unittest.TestCase):

    # ------------------------------------------------------------------
    # Windows – success
    # ------------------------------------------------------------------
    @patch("rat.commands.hashdump.Path.read_bytes")
    @patch("rat.commands.hashdump.Path.unlink")
    @patch("rat.commands.hashdump.subprocess.run")
    @patch("ctypes.windll.shell32.IsUserAnAdmin")      # target the real ctypes
    @patch("rat.commands.hashdump.platform.system")
    def test_windows_hashdump_success(
        self, mock_system, mock_admin, mock_run, mock_unlink, mock_read_bytes
    ):
        mock_system.return_value = "Windows"
        mock_admin.return_value = True
        mock_run.return_value = MagicMock(returncode=0)
        mock_read_bytes.return_value = b"fake hive data"

        cmd = HashdumpCommand()
        result = cmd.execute("")

        self.assertIn("Windows SAM hive (base64):", result)
        # base64 of "fake hive data"
        self.assertIn("ZmFrZSBoaXZlIGRhdGE=", result)

        mock_run.assert_called_with(
            ["reg", "save", "HKLM\\SAM", "C:\\Windows\\Temp\\sam_dump", "/y"],
            capture_output=True, text=True, timeout=10
        )

    # ------------------------------------------------------------------
    # Windows – reg save fails
    # ------------------------------------------------------------------
    @patch("rat.commands.hashdump.Path.unlink")
    @patch("rat.commands.hashdump.subprocess.run")
    @patch("ctypes.windll.shell32.IsUserAnAdmin")
    @patch("rat.commands.hashdump.platform.system")
    def test_windows_reg_save_failure(
        self, mock_system, mock_admin, mock_run, mock_unlink
    ):
        mock_system.return_value = "Windows"
        mock_admin.return_value = True
        mock_run.return_value = MagicMock(returncode=1, stderr="Access denied")

        cmd = HashdumpCommand()
        result = cmd.execute("")
        self.assertEqual(result, "reg save failed: Access denied")

    # ------------------------------------------------------------------
    # Windows – not admin
    # ------------------------------------------------------------------
    @patch("ctypes.windll.shell32.IsUserAnAdmin")
    @patch("rat.commands.hashdump.platform.system")
    def test_windows_not_admin(self, mock_system, mock_admin):
        mock_system.return_value = "Windows"
        mock_admin.return_value = False

        cmd = HashdumpCommand()
        result = cmd.execute("")
        self.assertEqual(result, "Administrator privileges required.")

    # ------------------------------------------------------------------
    # Linux – success (require root)
    # ------------------------------------------------------------------
    @patch("rat.commands.hashdump.Path.read_text")
    @patch("rat.commands.hashdump.Path.exists")
    @patch("rat.commands.hashdump.platform.system")
    @patch("os.geteuid", create=True)          # inject geteuid on Windows
    def test_linux_hashdump_success(
        self, mock_geteuid, mock_system, mock_exists, mock_read_text
    ):
        mock_system.return_value = "Linux"
        mock_geteuid.return_value = 0          # root
        mock_exists.return_value = True
        mock_read_text.return_value = "root:x:0:0::/root:/bin/bash\nuser1:$6$hash:1000:1000::/home/user1:/bin/bash\n"

        cmd = HashdumpCommand()
        result = cmd.execute("")

        self.assertIn("root:x:0:0", result)
        self.assertIn("user1:$6$hash", result)

    # ------------------------------------------------------------------
    # Linux – shadow not found
    # ------------------------------------------------------------------
    @patch("rat.commands.hashdump.Path.exists")
    @patch("rat.commands.hashdump.platform.system")
    def test_linux_shadow_not_found(self, mock_system, mock_exists):
        mock_system.return_value = "Linux"
        mock_exists.return_value = False

        cmd = HashdumpCommand()
        result = cmd.execute("")
        self.assertEqual(result, "Error: /etc/shadow not found")

    # ------------------------------------------------------------------
    # Linux – not root
    # ------------------------------------------------------------------
    @patch("os.geteuid", create=True)
    @patch("rat.commands.hashdump.Path.exists")
    @patch("rat.commands.hashdump.platform.system")
    def test_linux_not_root(self, mock_system, mock_exists, mock_geteuid):
        mock_system.return_value = "Linux"
        mock_exists.return_value = True
        mock_geteuid.return_value = 1000          # normal user

        cmd = HashdumpCommand()
        result = cmd.execute("")
        self.assertEqual(result, "Root privileges required. Run the client with sudo.")

    # ------------------------------------------------------------------
    # Linux – permission error on read
    # ------------------------------------------------------------------
    @patch("rat.commands.hashdump.Path.read_text")
    @patch("os.geteuid", create=True)
    @patch("rat.commands.hashdump.Path.exists")
    @patch("rat.commands.hashdump.platform.system")
    def test_linux_permission_denied(
        self, mock_system, mock_exists, mock_geteuid, mock_read_text
    ):
        mock_system.return_value = "Linux"
        mock_exists.return_value = True
        mock_geteuid.return_value = 0            # root (but read fails)
        mock_read_text.side_effect = PermissionError("Permission denied")

        cmd = HashdumpCommand()
        result = cmd.execute("")
        self.assertIn("Error: cannot read /etc/shadow", result)

    # ------------------------------------------------------------------
    # Unsupported OS
    # ------------------------------------------------------------------
    @patch("rat.commands.hashdump.platform.system")
    def test_unsupported_os(self, mock_system):
        mock_system.return_value = "FreeBSD"

        cmd = HashdumpCommand()
        result = cmd.execute("")
        self.assertEqual(result, "Unsupported OS: FreeBSD")


if __name__ == "__main__":
    unittest.main()