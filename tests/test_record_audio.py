import unittest
from unittest.mock import patch
import base64

from rat.commands.record_audio import AudioRecordCommand


class TestAudioRecordCommand(unittest.TestCase):

    def setUp(self):
        self.cmd = AudioRecordCommand()

    # ------------------------------------------------------------------
    # Start – successful
    # ------------------------------------------------------------------
    @patch("rat.commands.record_audio.recorder.start")
    def test_start_success(self, mock_start):
        mock_start.return_value = "Recording started"

        result = self.cmd.execute("start")

        self.assertEqual(result, "RECORD\nOK\nEOF")
        mock_start.assert_called_once()

    # ------------------------------------------------------------------
    # Start – already recording
    # ------------------------------------------------------------------
    @patch("rat.commands.record_audio.recorder.start")
    def test_start_already_recording(self, mock_start):
        mock_start.return_value = "Already recording"

        result = self.cmd.execute("start")

        self.assertIn("RECORD\nERROR\n", result)
        self.assertIn("Already recording", result)

    # ------------------------------------------------------------------
    # Start – microphone error
    # ------------------------------------------------------------------
    @patch("rat.commands.record_audio.recorder.start")
    def test_start_mic_error(self, mock_start):
        mock_start.return_value = "Microphone error – no device found: ..."

        result = self.cmd.execute("start")

        self.assertIn("RECORD\nERROR\n", result)
        self.assertIn("Microphone error", result)

    # ------------------------------------------------------------------
    # Stop – successful, returns audio bytes
    # ------------------------------------------------------------------
    @patch("rat.commands.record_audio.recorder.stop")
    def test_stop_success(self, mock_stop):
        fake_wav = b"RIFF....WAVE..."  # minimal WAV header
        mock_stop.return_value = fake_wav

        result = self.cmd.execute("stop")

        expected_encoded = base64.b64encode(fake_wav).decode()
        expected = f"AUDIO\nOK\n{expected_encoded}\nEOF"
        self.assertEqual(result, expected)
        mock_stop.assert_called_once()

    # ------------------------------------------------------------------
    # Stop – no recording active (empty bytes)
    # ------------------------------------------------------------------
    @patch("rat.commands.record_audio.recorder.stop")
    def test_stop_no_active_recording(self, mock_stop):
        mock_stop.return_value = b""

        result = self.cmd.execute("stop")

        self.assertIn("AUDIO\nERROR\nNo recording active", result)

    # ------------------------------------------------------------------
    # Stop – exception during stop
    # ------------------------------------------------------------------
    @patch("rat.commands.record_audio.recorder.stop")
    def test_stop_exception(self, mock_stop):
        mock_stop.side_effect = Exception("Some unexpected error")

        result = self.cmd.execute("stop")

        self.assertIn("AUDIO\nERROR\nSome unexpected error", result)

    # ------------------------------------------------------------------
    # Unknown subcommand
    # ------------------------------------------------------------------
    def test_unknown_subcommand(self):
        result = self.cmd.execute("pause")
        self.assertIn("Usage: record_audio start|stop", result)

        result = self.cmd.execute("")
        self.assertIn("Usage: record_audio start|stop", result)


if __name__ == "__main__":
    unittest.main()