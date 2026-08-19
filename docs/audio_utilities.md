## audio_capture
- uses pyaudio and sets up input device for audio capture 
- contains stop and start function for opening the channels and the other for a clean shutdown.
- *read function* : don't know if it is being used

## audio_segmentor
- segments audio into a new chunk if there is silence above a specified time limit threshold, and the silence is also decided by the a threshold too, which also can be changed. 
- The rms of the input audio signal is compared with the threshold value
- The function cuts down the audio data between 2 silence segments, and returns the audio segment.

## audio_resampler
- changes the sample rate of the audio data
- The microphone I am using outputs 48000 hz data, this function resamples it down to 16hz. Makes the data a little lighter, efficient for inference.
- *It is written as a seperate class I guess I can combine this and the segmentor together*





