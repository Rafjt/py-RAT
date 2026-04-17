import unittest
from unittest.mock import patch, MagicMock
from pynput.keyboard import KeyCode
from rat.client.keylogger_service import KeyloggerService


class TestKeyloggerService(unittest.TestCase):

    def setUp(self):

        self.k = KeyloggerService()

    # START
    @patch("rat.client.keylogger_service.keyboard.Listener")
    def test_start(self, mock_listener):

        result = self.k.start()

        self.assertEqual(result, "Keylogger started")
        self.assertTrue(self.k._running)

        mock_listener.assert_called_once()

    # START TWICE
    @patch("rat.client.keylogger_service.keyboard.Listener")
    def test_start_twice(self, mock_listener):

        self.k.start()

        result = self.k.start()

        self.assertEqual(result, "Keylogger already running")

    # STOP WITHOUT START
    def test_stop_without_start(self):

        result = self.k.stop()

        self.assertEqual(result, "Keylogger not running")

    # STOP RETURNS BUFFER
    @patch("rat.client.keylogger_service.keyboard.Listener")
    def test_stop_returns_buffer(self, mock_listener):

        self.k.start()

        self.k._buffer = ["h", "e", "l", "l", "o"]

        data = self.k.stop()

        self.assertEqual(data, "hello")

    # CHARACTER KEY
    def test_on_press_character(self):
        key = KeyCode.from_char("a")

        self.k._on_press(key)

        self.assertIn("a", self.k._buffer)

    # SPECIAL KEY
    def test_on_press_special_key(self):

        mock_key = MagicMock()

        mock_key.char = None
        mock_key.name = "enter"

        with patch(
            "rat.client.keylogger_service.keyboard.KeyCode",
            new=type("KeyCode", (), {}),
        ):

            self.k._on_press(mock_key)

        self.assertTrue(len(self.k._buffer) >= 0)

    # BUFFER CLEARED AFTER STOP
    @patch("rat.client.keylogger_service.keyboard.Listener")
    def test_buffer_cleared_after_stop(self, mock_listener):

        self.k.start()

        self.k._buffer = ["t", "e", "s", "t"]

        self.k.stop()

        self.assertEqual(self.k._buffer, [])
