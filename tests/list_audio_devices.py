import pyaudio

p = pyaudio.PyAudio()

print("PyAudio devices:\n")

for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)

    print(
        f"{i}: {info['name']} | "
        f"inputs={info['maxInputChannels']} | "
        f"outputs={info['maxOutputChannels']} | "
        f"rate={info['defaultSampleRate']}"
    )

p.terminate()
