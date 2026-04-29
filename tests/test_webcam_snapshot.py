import base64
import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from rat.commands.webcam_snapshot import WebcamSnapshotCommand


@pytest.fixture
def cmd():
    return WebcamSnapshotCommand()


def test_webcam_snapshot_success(cmd):

    fake_frame = np.zeros((100, 100, 3), dtype=np.uint8)

    mock_capture = MagicMock()
    mock_capture.isOpened.return_value = True
    mock_capture.read.return_value = (True, fake_frame)

    fake_buffer = b"fakeimage"

    with patch("cv2.VideoCapture", return_value=mock_capture):
        with patch("cv2.imencode", return_value=(True, fake_buffer)):

            result = cmd.execute("")

    assert result.startswith("WEBCAM\nOK\n")

    encoded = result.split("\n")[2]

    decoded = base64.b64decode(encoded)

    assert decoded == fake_buffer


def test_camera_not_available(cmd):

    mock_capture = MagicMock()
    mock_capture.isOpened.return_value = False

    with patch("cv2.VideoCapture", return_value=mock_capture):

        result = cmd.execute("")

    assert result == ("WEBCAM\nERROR\nCamera not available")


def test_capture_failed(cmd):

    mock_capture = MagicMock()
    mock_capture.isOpened.return_value = True
    mock_capture.read.return_value = (False, None)

    with patch("cv2.VideoCapture", return_value=mock_capture):

        result = cmd.execute("")

    assert result == ("WEBCAM\nERROR\nFailed to capture frame")


def test_encoding_failed(cmd):

    fake_frame = np.zeros((10, 10, 3), dtype=np.uint8)

    mock_capture = MagicMock()
    mock_capture.isOpened.return_value = True
    mock_capture.read.return_value = (True, fake_frame)

    with patch("cv2.VideoCapture", return_value=mock_capture):
        with patch("cv2.imencode", return_value=(False, None)):

            result = cmd.execute("")

    assert result == ("WEBCAM\nERROR\nEncoding failed")


def test_exception_handled(cmd):

    with patch("cv2.VideoCapture", side_effect=Exception("boom")):

        result = cmd.execute("")

    assert result.startswith("WEBCAM\nERROR\n")
    assert "boom" in result
