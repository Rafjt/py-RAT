import mss
import mss.tools


class ScreenshotService:

    def capture(self) -> bytes:

        with mss.mss() as sct:

            monitor = sct.monitors[1]

            screenshot = sct.grab(monitor)

            return mss.tools.to_png(screenshot.rgb, screenshot.size)
