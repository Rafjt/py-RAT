# Ce module implémente un enregistreur audio simple basé sur un microphone.
# Il permet de démarrer un enregistrement en arrière-plan (thread),
# accumuler les données audio, puis les convertir en fichier WAV en mémoire
# L'enregistrement receuillis sera ensuite envoyé au serveur

import threading
import io
import wave
import soundcard as sc
import numpy as np


class AudioRecorder:
    def __init__(self):
        # Microphone actif
        self._mic = None

        # Buffer contenant les chunks audio capturés
        self._frames = []

        # Flag indiquant si l’enregistrement est en cours
        self._recording = False

        # Thread dédié à la capture audio
        self._thread = None

    def start(self) -> str:
        # Empêche de lancer plusieurs enregistrements simultanés
        if self._recording:
            return "Already recording"

        # Récupère le micro par défaut du système
        try:
            self._mic = sc.default_microphone()
        except Exception as e:
            return f"Microphone error – no device found: {e}"

        # Reset du buffer audio
        self._frames = []
        self._recording = True

        # Lance la capture dans un thread pour ne pas bloquer le programme principal
        self._thread = threading.Thread(target=self._record_loop, daemon=True)
        self._thread.start()

        return "Recording started"

    def _record_loop(self):
        # Paramètres audio standard (qualité CD)
        samplerate = 44100

        # Ouverture du flux d’enregistrement
        with self._mic.recorder(samplerate=samplerate, channels=1) as rec:

            # Capture en continu tant que _recording est vrai
            while self._recording:
                # Capture par petits chunks (~100ms)
                data = rec.record(int(samplerate * 0.1))

                # Sécurité si le périphérique retourne None
                if data is None:
                    break

                # Stockage du chunk audio
                self._frames.append(data)

    def stop(self) -> bytes:
        # Si aucun enregistrement en cours → rien à retourner
        if not self._recording:
            return b""

        # Stop propre du thread
        self._recording = False
        self._thread.join(timeout=2)

        # Si aucun audio capturé → retour vide
        if not self._frames:
            return b""

        # Concatène tous les chunks en un seul tableau
        audio = np.concatenate(self._frames, axis=0)

        # Conversion float → int16 (format PCM standard)
        audio_int16 = (audio * 32767).astype(np.int16)

        # Conversion en bytes bruts
        raw_bytes = audio_int16.tobytes()

        # Création d’un fichier WAV en mémoire
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wf:
            wf.setnchannels(1)  # mono
            wf.setsampwidth(2)  # 16 bits
            wf.setframerate(44100)  # fréquence d’échantillonnage
            wf.writeframes(raw_bytes)

        # Repositionne le buffer au début
        wav_buffer.seek(0)

        # Retourne le contenu du WAV prêt à être envoyé
        return wav_buffer.read()


# Instance globale réutilisable (évite de recréer un recorder à chaque fois)
recorder = AudioRecorder()
