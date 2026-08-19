import time
import numpy as np

from audio_capture import AudioCapture

DEVICE_INDEX = 0
SAMPLE_RATE = 48000
CHANNELS = 1
CHUNK_SIZE = 1024

def calculate_rms(raw_data):
    
    samples = np.frombuffer(raw_data,dtype=np.int16)

    return np.sqrt(np.mean(samples.astype(np.float32) ** 2))

def main():

    capture = AudioCapture(device_index=DEVICE_INDEX,
                           sample_rate=SAMPLE_RATE,
                           channels=CHANNELS,
                           chunk_size=CHUNK_SIZE)

    capture.start()

    print("Listening...")
    print("Speak..")

    print("Ctrl + c to stop\n")

    try:
        while True:
            data = capture.read()
            rms = calculate_rms(data)

            print(f"\rRMS : {rms:0.1f}", end="", flush=True)

            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\n")

    finally:
        capture.stop()


if __name__ == "__main__":
    main()
