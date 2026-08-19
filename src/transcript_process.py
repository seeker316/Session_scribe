from datetime import datetime
import signal

from session_manager import SessionManager
from events import TRANSCRIPT_SAVED
from logger import setup_logger

def transcript_worker(text_queue, session, status_queue):
    signal.signal( signal.SIGINT, signal.SIG_IGN)
    logger = setup_logger()

    logger.info("Transcript writer started")
    logger.info(
        "Writing transcript to: %s",
        session.transcript_file)

    logger.info("Text queue drained")
    
    transcript_file = open(
        session.transcript_file,
        "a",
        encoding="utf-8")
    
    session_manager = SessionManager()
    try:
        while True:
            item = text_queue.get()

            if item is None:
                print(
                    "[TRANSCRIPT] "
                    "Text queue drained.")
                break

            text = item["text"]
            timestamp = datetime.now().strftime("%H:%M:%S")
            inference_time = item["inference_time"]
            audio_duration = item["audio_duration"]
        
            transcript_file.write(
                f"[{timestamp}] {text}\n"
            )
            transcript_file.flush()

            session_manager.update_last_active(session)
            status_queue.put({
                "type": TRANSCRIPT_SAVED,
                "text": text,
                "timestamp": timestamp})

            logger.info(
                "Transcript saved: "
                "[%s] %s | "
                "Audio: %.2fs | "
                "Inference: %.2fs",
                timestamp,
                text,
                audio_duration,
                inference_time
            )
            
    finally:
        transcript_file.close()
        logger.info("Transcript writer stopped")

