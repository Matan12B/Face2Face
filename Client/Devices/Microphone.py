import queue
import pyaudio
import wave
import numpy 


class Microphone:
    def __init__(self, volume, rate=16000, channels=1, chunk=1024, device_index=None):
        self.running = False
        self.is_muted = True
        self.records = queue.Queue()  # FIXED
        self.volume = self._validate_volume(volume)

        # Audio settings
        self.rate = rate
        self.channels = channels
        self.chunk = chunk
        self.device_index = device_index

        # PyAudio setup
        self.audio = pyaudio.PyAudio()
        self.stream = None

    def _validate_volume(self, volume: int) -> int:
        if not 0 <= volume <= 100:
            raise ValueError("Volume must be between 0 and 100.")
        return volume

    def start(self):
        if self.running:
            return

        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
            input_device_index=self.device_index
        )

        self.running = True
        print("Microphone started.")

    def stop(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        self.running = False
        print("Microphone stopped.")

    def set_volume(self, volume):
        self.volume = self._validate_volume(volume)

    def record(self):
        if not self.running:
            raise RuntimeError("Microphone is not active.")
        data = self.stream.read(self.chunk, exception_on_overflow=False)
        if self.is_muted:
            return b'\x00' * len(data)
        data = self._apply_volume(data)
        return data

    def _apply_volume(self, data):
        """

        :param data:
        :return:
        """
        # Convert bytes to numpy array
        audio_data = numpy.frombuffer(data, dtype=numpy.int16)
        # Scale by volume (0–100)
        scaled = (audio_data * (self.volume / 100)).astype(numpy.int16)
        return scaled.tobytes()


    def unmute(self):
        self.is_muted = False
        print("Microphone is unmuted.")

    def mute(self):
        self.is_muted = True
        print("Microphone is muted.")

    def close(self):
        self.stop()
        self.audio.terminate()


def main():
    from AudioOutputDevice import AudioOutput

    print("Starting microphone test...")
    print("This will capture audio from your microphone and play it back through speakers.")
    print("Press Ctrl+C to stop.\n")

    # Create microphone and audio output
    mic = Microphone(volume=80, rate=16000, channels=1)
    speaker = AudioOutput(rate=16000, channels=1)

    try:
        mic.start()
        mic.unmute()

        print("Recording and playing back... (Press Ctrl+C to stop)")

        while True:
            # Record audio from microphone
            audio_data = mic.record()

            # Play it back through speakers
            speaker.play_bytes(audio_data)

    except KeyboardInterrupt:
        print("\nStopping...")

    finally:
        mic.close()
        speaker.stop()
        print("Audio test completed.")


if __name__ == "__main__":
    main()