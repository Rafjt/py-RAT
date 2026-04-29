import cv2
import base64


class WebcamSnapshotCommand:

    name = "webcam_snapshot"

    def execute(self, args: str) -> str:

        try:

            cap = cv2.VideoCapture(0)

            if not cap.isOpened():

                return "WEBCAM\nERROR\nCamera not available"

            ret, frame = cap.read()

            cap.release()

            if not ret:

                return "WEBCAM\nERROR\nFailed to capture frame"

            success, buffer = cv2.imencode(".jpg", frame)

            if not success:

                return "WEBCAM\nERROR\nEncoding failed"

            encoded = base64.b64encode(buffer).decode()

            return "WEBCAM\n" "OK\n" + encoded

        except Exception as e:

            return "WEBCAM\n" "ERROR\n" + str(e)
