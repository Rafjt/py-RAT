import threading
import io
import wave
import soundcard as sc

class AudioRecorder:
    def __init__(self):
        self._mic = None
        self._frames = []
        self._recording = False
        self._thread = None

    def start(self) -> str:
        if self._recording:
            return "Already recording"

        try:
            self._mic = sc.default_microphone()
        except Exception as e:
            return f"Microphone error – no device found: {e}"

        self._frames = []          # reset buffer on new start
        self._recording = True
        self._thread = threading.Thread(target=self._record_loop, daemon=True)
        self._thread.start()
        return "Recording started"

    def _record_loop(self):
        samplerate = 44100
        with self._mic.recorder(samplerate=samplerate, channels=1) as rec:
            while self._recording:
                data = rec.record(int(samplerate * 0.1))   # ~0.1 sec chunks
                if data is None:
                    break
                self._frames.append(data)

    def stop(self) -> bytes:
        if not self._recording:
            return b""
        self._recording = False
        self._thread.join(timeout=2)

        if not self._frames:
            return b""

        import numpy as np
        audio = np.concatenate(self._frames, axis=0)
        audio_int16 = (audio * 32767).astype(np.int16)
        raw_bytes = audio_int16.tobytes()

        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            wf.writeframes(raw_bytes)
        wav_buffer.seek(0)
        return wav_buffer.read()


recorder = AudioRecorder()