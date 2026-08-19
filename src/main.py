import multiprocessing
import signal

from capture_process import capture_worker
from inference_process import inference_worker
from transcript_process import transcript_worker
from session_manager import SessionManager
from tui import SessionSelector
from summarizer import SessionSummarizer

from config import (
    AUDIO_QUEUE_SIZE,
    TEXT_QUEUE_SIZE,
    STATUS_QUEUE_SIZE,
    CAPTURE_SHUTDOWN_TIMEOUT,
    INFERENCE_SHUTDOWN_TIMEOUT,
    TRANSCRIPT_SHUTDOWN_TIMEOUT,
    FORCE_TERMINATE_TIMEOUT,
)

from logger import setup_logger
logger = setup_logger()

class PipelineManager:
    
    def __init__(self):
        self.audio_queue = None
        self.text_queue = None
        self.status_queue = None
        
        self.shutdown_event = None
        self.pause_event = None
        
        self.capture_process = None
        self.inference_process = None
        self.transcript_process = None

        self.running = False
    
    def start(self, session):
        if self.running:
            logger.warning("Pipeline already running")
            return
        
        logger.info("Starting session: %s_%s", session.name, session.session_id)

        self.audio_queue = multiprocessing.Queue(maxsize=AUDIO_QUEUE_SIZE)
        self.text_queue = multiprocessing.Queue(maxsize=TEXT_QUEUE_SIZE)
        self.status_queue = multiprocessing.Queue(maxsize=STATUS_QUEUE_SIZE)
            
        self.shutdown_event = multiprocessing.Event()
        self.pause_event = multiprocessing.Event()

        self.capture_process = multiprocessing.Process(
                            target=capture_worker,
                            args=(
                                self.audio_queue,
                                self.shutdown_event,
                                self.status_queue,
                                self.pause_event
                            ),
                            name="CaptureProcess"
                        )


        self.inference_process = multiprocessing.Process(
                            target=inference_worker,
                            args=(
                                self.audio_queue,
                                self.text_queue,
                                self.status_queue
                            ),
                            name="InferenceProcess"
                        )
    
        self.transcript_process = multiprocessing.Process(
                            target=transcript_worker,
                            args=(
                                self.text_queue,
                                session,
                                self.status_queue
                            ),
                            name="TranscriptProcess"
                        )
        
        self.capture_process.start()
        self.inference_process.start()
        self.transcript_process.start()

        self.running = True

    def pause(self):
        if self.running:
            self.pause_event.set()

    def resume(self):
        if self.running:
            self.pause_event.clear()
            
    def shutdown(self):
        if not self.running:
            return

        logger.info("Pipeline shutdown requested")

        self.shutdown_event.set()
        self.capture_process.join(timeout=CAPTURE_SHUTDOWN_TIMEOUT)
 
        if self.capture_process.is_alive():
            logger.warning("Force stopping capture process")
            self.capture_process.terminate()
            self.capture_process.join(timeout=FORCE_TERMINATE_TIMEOUT)

        self.inference_process.join(timeout=INFERENCE_SHUTDOWN_TIMEOUT)
        if self.inference_process.is_alive():
            logger.warning("Force stopping inference process")
            self.inference_process.terminate()
            self.inference_process.join(timeout=FORCE_TERMINATE_TIMEOUT)
        
        self.transcript_process.join(timeout=TRANSCRIPT_SHUTDOWN_TIMEOUT)    
        if self.transcript_process.is_alive():
            logger.warning("Force stopping transcripting process")
            self.transcript_process.terminate()
            self.transcript_process.join(timeout=FORCE_TERMINATE_TIMEOUT)
        
        self.audio_queue.close()
        self.text_queue.close()
        self.status_queue.close()

        self.audio_queue.join_thread()
        self.text_queue.join_thread()
        self.status_queue.join_thread()

        self.capture_process = None
        self.inference_process = None
        self.transcript_process = None

        self.audio_queue = None
        self.text_queue = None
        self.status_queue = None
        self.shutdown_event = None
        self.pause_event = None

        self.running = False
        logger.info("Pipeline shutdown complete")


def main():
    session_manager = SessionManager()
    pipeline = PipelineManager()
    summarizer = SessionSummarizer()

    def handle_signal(signum, frame):
        logger.info("Received signal %s", signum)
        pipeline.shutdown()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
        
    def session_selected(session):
        pipeline.start(session)
        #
        # def stop_session():
        #     pipeline.shutdown()
        #
        #     def summarize(): 
        #         summarizer.summarize(session)
        #
        #     threading.Thread(target=summarize, daemon=True).start()
 
        def stop_session(on_status):
            on_status("Ending session...")
            pipeline.shutdown()

            on_status("Summarizing session...")
            summarizer.summarize(session)
            on_status("Summary saved")

            # threading.Thread(target=summarize, daemon=True).start()
            #
        def pause_session():
            pipeline.pause()

        def resume_session():
            pipeline.resume()
        
        return (pipeline.status_queue, stop_session, pause_session, resume_session)
    
    app = SessionSelector(
        session_manager=session_manager,
        on_session_selected=session_selected)
    try:
        app.run()

    finally:
        pipeline.shutdown()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
