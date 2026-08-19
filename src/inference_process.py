import time
import numpy as np
import torch
import whisper

from events import (
    INFERENCE_STARTED,
    INFERENCE_COMPLETED,)

from config import (
    OUTPUT_SAMPLE_RATE,
    WHISPER_MODEL_NAME,
    WHISPER_LANGUAGE,)

from logger import setup_logger

def inference_worker(audio_queue, text_queue, status_queue):
    
    logger = setup_logger()
    logger.info("Loading Whisper model: %s", WHISPER_MODEL_NAME)
    
    model = whisper.load_model(WHISPER_MODEL_NAME)

    logger.info("Whisper model loaded")
    
    while True:
        segment = audio_queue.get()

        if segment is None:
            logger.info("Audio queue drained")            
            text_queue.put(None)
            break

        duration = (len(segment) / (OUTPUT_SAMPLE_RATE * 2))

        logger.info(
            "Received 16 kHz segment: "
            "%.2f sec (%d bytes)",
            duration,
            len(segment))

        audio_int16 = np.frombuffer(segment, dtype=np.int16)

        
        audio = (audio_int16.astype(np.float32)/ 32768.0)
        
        duration = (len(audio) / OUTPUT_SAMPLE_RATE)
        
        
        logger.info(
            "Transcribing %.2f s of audio",
            duration)

        start_time = time.perf_counter()
        
        status_queue.put({"type": INFERENCE_STARTED, "audio_duration": duration})
        result = model.transcribe(audio, language=WHISPER_LANGUAGE, fp16=torch.cuda.is_available())

        elapsed_time = (
            time.perf_counter()
            - start_time)
        
        rtf = duration / elapsed_time

        text = result["text"].strip()
        status_queue.put({
            "type": INFERENCE_COMPLETED,
            "text": text,
            "audio_duration": duration,
            "inference_time": elapsed_time})

        logger.info(
            "Transcription completed: "
            "audio=%.2fs, inference=%.2fs, "
            "RTF=%.2f, text=%r",
            duration,
            elapsed_time,
            rtf,
            text
        )

        text_queue.put({
            "text": text,
            "inference_time": elapsed_time,
            "audio_duration": duration
        })

    logger.info("Inference process stopped")
  
