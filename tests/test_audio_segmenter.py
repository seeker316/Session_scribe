from audio_capture import AudioCapture
from audio_segmenter import AudioSegmenter

DEVICE_INDEX = 0
SAMPLE_RATE = 48000
CHANNELS = 1
CHUNK_SIZE = 1024

ENERGY_THRESHOLD = 7000
SILENCE_DURATION = 1.5

def main():
    capture = AudioCapture(
            device_index = DEVICE_INDEX,
            sample_rate = SAMPLE_RATE,
            channels = CHANNELS,
            chunk_size = CHUNK_SIZE
            )

    segmenter = AudioSegmenter(
            sample_rate=SAMPLE_RATE,
            channels=CHANNELS,
            energy_threshold=ENERGY_THRESHOLD,
            silence_duration=SILENCE_DURATION
            )
    
    capture.start()

    print("Listening...")

    print("Speak a sentence..")

    print("Ctrl + C to stop\n")

    try:
        while True:
            audio_data = capture.read()
            segment = segmenter.process(audio_data)

            if segment is not None:
                duration = (len(segment) / (SAMPLE_RATE * 2 * CHANNELS))

                print(f"\n[SEGMENT]" f"{duration:.2f} seconds")
    
    except KeyboardInterrupt:
        print("\nStopping...")

    finally:
        capture.stop()


if __name__ == "__main__":
    main()
