-  Contains the inference worker method which
	- loads the whisper model as per the config.
	- picks up a segment from the audio_queue,
	- converts those samples to `float32` and normalizes them to roughly `[-1, 1]`, which Whisper expects.
	- then feeds the audio data into the model, which transcribes it into text
	- The text is then pushed into the text_queue


> audio segment contains raw PCM bytes, these bytes are represented with 16-bit integers. it is a standard for interpreting the raw bytes correctly as audio samples.

