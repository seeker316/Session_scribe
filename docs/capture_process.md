- contains capture_worker function which uses [[audio_utilities]] to do 
	- audio_capture [[audio_utilities#audio_capture | audio_capture]]
	- audio_segmentation [[audio_utilities#audio_segmentor | audio_segmentation]]
	- and audio_resampling [[audio_utilities#audio_resampler | audio_resampler]]
- the function uses and audio_queue which is a multiprocessing queue, to feed the processed data which is later used by other processes.
- also updates states in a status queue, which is also a multi processing queue.

- [x] will have to take a look at the shut downs hapenning*

