import pyaudio
from config import (
    INPUT_SAMPLE_RATE,
    AUDIO_CHANNELS,
    AUDIO_CHUNK_SIZE,
)
from logger import setup_logger
logger = setup_logger()

class AudioCapture:
    def __init__(self, device_index=None, sample_rate=INPUT_SAMPLE_RATE, channels=AUDIO_CHANNELS, chunk_size=AUDIO_CHUNK_SIZE):
        self.device_index= device_index
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size

        self.audio = None
        self.stream = None

    def start(self):
        self.audio = pyaudio.PyAudio()

        self.stream = self.audio.open(format=pyaudio.paInt16,
                                      channels=self.channels,
                                      rate=self.sample_rate,
                                      input=True,
                                      input_device_index=self.device_index,
                                      frames_per_buffer=self.chunk_size)

        logger.info(
            "Audio capture started: %d Hz, %d channels",
            self.sample_rate,
            self.channels)

    def read(self):
        if self.stream is None:
            raise RuntimeError(
                    "AudioCapture has not been started")

        return self.stream.read(self.chunk_size, exception_on_overflow=False)

    def stop(self):
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        if self.audio is not None:
            self.audio.terminate()
            self.audio = None

        logger.info("Audio capture stopped")
