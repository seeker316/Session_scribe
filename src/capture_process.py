import signal
import time

from audio_capture import AudioCapture
from audio_segmenter import AudioSegmenter
from audio_resampler import AudioResampler
from events import (
    CAPTURE_STARTED,
    CAPTURE_STOPPED,
    SEGMENT_CREATED,
)

from config import (
    INPUT_SAMPLE_RATE,
    OUTPUT_SAMPLE_RATE,
    AUDIO_CHANNELS,
    AUDIO_CHUNK_SIZE,
    AUDIO_DEVICE_INDEX,
    AUDIO_SEGMENT_ENERGY_THRESHOLD,
    AUDIO_SEGMENT_SILENCE_DURATION,
    RMS_UPDATE_INTERVAL,
)
from logger import setup_logger

def capture_worker(audio_queue, shutdown_event, status_queue, pause_event):
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    last_rms_update = 0.0
    logger = setup_logger()

    capture = AudioCapture(device_index=AUDIO_DEVICE_INDEX,
                           sample_rate=INPUT_SAMPLE_RATE,
                           channels=AUDIO_CHANNELS,
                           chunk_size=AUDIO_CHUNK_SIZE)
    
    segmenter = AudioSegmenter(sample_rate=INPUT_SAMPLE_RATE,
                               channels=AUDIO_CHANNELS,
                               energy_threshold=AUDIO_SEGMENT_ENERGY_THRESHOLD,
                               silence_duration=AUDIO_SEGMENT_SILENCE_DURATION)
    
    resampler = AudioResampler(input_rate=INPUT_SAMPLE_RATE, output_rate = OUTPUT_SAMPLE_RATE)

    capture.start()
    status_queue.put({"type": CAPTURE_STARTED})
    logger.info("Capture process started")

    try:
        while not shutdown_event.is_set():

            if pause_event.is_set():
                time.sleep(0.05)
                continue
            
            audio_data = capture.read()
            segment, rms = segmenter.process(audio_data)

            now = time.monotonic()
            if now - last_rms_update >= 0.1:
                status_queue.put({"type": "rms", "value": float(rms)})
                last_rms_update = now
            
            if segment is not None:
                input_duration = (len(segment) / (INPUT_SAMPLE_RATE * 2))
                resampled_segment = resampler.resample(segment)

                output_duration = (len(resampled_segment)/ (OUTPUT_SAMPLE_RATE * 2))

                audio_queue.put(resampled_segment)
                status_queue.put({
                    "type": SEGMENT_CREATED,
                    "duration": (
                        len(resampled_segment)
                        / 2
                        / OUTPUT_SAMPLE_RATE)})

                logger.info(
                    "Segment resampled: "
                    "%d bytes (%.2fs) -> "
                    "%d bytes (%.2fs)",
                    len(segment),
                    input_duration,
                    len(resampled_segment),
                    output_duration
                )

    finally:
        capture.stop()
        audio_queue.put(None) 
        status_queue.put({"type": CAPTURE_STOPPED})
        logger.info("Capture process stopped")


