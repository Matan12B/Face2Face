import pyaudio

class AudioOutput:
    def __init__(self, rate=44100, channels=2, format=pyaudio.paInt16, device_index=None):
        """
        אתחול התקן הפלט.
        :param rate: קצב דגימה (למשל 44100Hz)
        :param channels: מספר ערוצים (1 למונו, 2 לסטריאו)
        :param device_index: ID של ההתקן (רמקול/אוזניות). אם None, ישתמש בברירת המחדל.
        """
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=format,
            channels=channels,
            rate=rate,
            output=True,
            output_device_index=device_index
        )

    def play_bytes(self, audio_bytes):
        """ מקבל bytes ומזרים אותם לרמקול/אוזניות """
        if self.stream.is_active():
            self.stream.write(audio_bytes)

    def stop(self):
        """ סגירת הזרם ושחרור משאבים """
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

    @staticmethod
    def list_devices():
        """ פונקציית עזר להצגת כל המכשירים המחוברים וה-ID שלהם """
        p = pyaudio.PyAudio()
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            print(f"ID {i}: {info['name']}")
        p.terminate()

# --- דוגמת שימוש ---
# 1. מצא את ה-ID של האוזניות/רמקולים שלך
# AudioOutput.list_devices()

# 2. צור מופע (למשל לאוזניות ב-ID 2)
# headphone = AudioOutput(device_index=2)
# headphone.play_bytes(some_byte_data)
