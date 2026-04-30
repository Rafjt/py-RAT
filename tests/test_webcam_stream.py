import pytest
from unittest.mock import MagicMock
from rat.commands.webcam_stream import WebcamStreamCommand


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.send = MagicMock()
    return client


def test_start_stream(mock_client):
    cmd = WebcamStreamCommand(mock_client)

    response = cmd.execute("start")

    assert cmd.streaming is True
    assert "OK" in response
    assert "Started" in response


def test_start_stream_already_running(mock_client):
    cmd = WebcamStreamCommand(mock_client)
    cmd.streaming = True

    response = cmd.execute("start")

    assert "ERROR" in response
    assert "Already streaming" in response


def test_stop_stream(mock_client):
    cmd = WebcamStreamCommand(mock_client)
    cmd.streaming = True

    response = cmd.execute("stop")

    assert cmd.streaming is False
    assert "OK" in response
    assert "Stopped" in response


def test_stop_stream_not_running(mock_client):
    cmd = WebcamStreamCommand(mock_client)

    response = cmd.execute("stop")

    assert "ERROR" in response
    assert "Not streaming" in response


def test_invalid_args(mock_client):
    cmd = WebcamStreamCommand(mock_client)

    response = cmd.execute("invalid")

    assert "ERROR" in response
    assert "Usage" in response
