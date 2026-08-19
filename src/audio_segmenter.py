import numpy as np
from config import (
    INPUT_SAMPLE_RATE,
    AUDIO_CHANNELS,
    AUDIO_SEGMENT_ENERGY_THRESHOLD,
    AUDIO_SEGMENT_SILENCE_DURATION,
)
class AudioSegmenter:

    def __init__(self, sample_rate=INPUT_SAMPLE_RATE, channels=AUDIO_CHANNELS, energy_threshold=AUDIO_SEGMENT_ENERGY_THRESHOLD , silence_duration=AUDIO_SEGMENT_SILENCE_DURATION):

        self.sample_rate = sample_rate
        self.channels = channels

        self.energy_threshold =  energy_threshold
        self.silence_duration = silence_duration

        self.silence_samples = int(sample_rate * silence_duration)

        self.recording = False

        self.buffer = []
        self.silence_samples_seen = 0
        self.rms = 0


    def process(self, audio_data):
        samples = np.frombuffer(audio_data, dtype=np.int16)
        
        self.rms = np.sqrt(np.mean(samples.astype(np.float32) ** 2))

        speech_detected = ( self.rms >= self.energy_threshold)
        
        if self.recording:
            self.buffer.append(audio_data)

            if speech_detected:
                self.silence_samples_seen=0
            
            else:
                self.silence_samples_seen += len(samples)

                if(self.silence_samples_seen >=self.silence_samples):
                    segment = b"".join(self.buffer)

                    self.buffer.clear()

                    self.recording = False

                    self.silence_samples_seen = 0

                    return segment, self.rms
        else:
            if speech_detected:
                self.recording = True
                self.buffer.append(audio_data)
                self.silence_samples_seen = 0

        return None, self.rms
