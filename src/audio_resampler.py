import numpy as np
from scipy.signal import resample_poly
from config import INPUT_SAMPLE_RATE, OUTPUT_SAMPLE_RATE

class AudioResampler:

    def __init__(self, input_rate=INPUT_SAMPLE_RATE, output_rate=OUTPUT_SAMPLE_RATE):
        self.input_rate = input_rate
        self.output_rate = output_rate

    def resample(self, audio_data):
        audio = np.frombuffer(audio_data, dtype=np.int16)

        resampled = resample_poly(audio, self.output_rate, self.input_rate)
        resampled = np.clip(resampled,-32768,32767).astype(np.int16)

        return resampled.tobytes()
