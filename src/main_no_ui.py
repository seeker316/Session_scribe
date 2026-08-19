import multiprocessing
import signal
import queue

from capture_process import capture_worker
from inference_process import inference_worker
from transcript_process import transcript_worker
from session_manager import SessionManager

from config import (
    AUDIO_QUEUE_SIZE,
    TEXT_QUEUE_SIZE,
    STATUS_QUEUE_SIZE,
    CAPTURE_SHUTDOWN_TIMEOUT,
    INFERENCE_SHUTDOWN_TIMEOUT,
    TRANSCRIPT_SHUTDOWN_TIMEOUT,
    FORCE_TERMINATE_TIMEOUT,
)


def main():

    session_manager = SessionManager()
    session = session_manager.create_session(
        "test"
    )

    audio_queue = multiprocessing.Queue(maxsize=AUDIO_QUEUE_SIZE)

    text_queue = multiprocessing.Queue(maxsize=TEXT_QUEUE_SIZE)

    status_queue = multiprocessing.Queue(maxsize=STATUS_QUEUE_SIZE)

    shutdown_event = multiprocessing.Event()
    pause_event = multiprocessing.Event()

    capture_process = multiprocessing.Process(
        target=capture_worker,
        args=(
            audio_queue,
            shutdown_event,
            status_queue,
            pause_event
        ),
        name="CaptureProcess"
    )

    inference_process = multiprocessing.Process(
        target=inference_worker,
        args=(
            audio_queue,
            text_queue,
            status_queue
        ),
        name="InferenceProcess"
    )

    transcript_process = multiprocessing.Process(
        target=transcript_worker,
        args=(
            text_queue,
            session,
            status_queue
        ),
        name="TranscriptProcess"
    )

    
    def shutdown(signum, frame):
        print(f"\n[MAIN] Received signal {signum}")
        shutdown_event.set()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    capture_process.start()
    inference_process.start()
    transcript_process.start()

    print("[MAIN] Processes started.")
    print("[MAIN] Headless pipeline running.\n")

    try:
        while not shutdown_event.is_set():
            try:
                event = status_queue.get(timeout=0.1)
                event_type = event.get("type")

                if event_type == "rms":
                    print(
                        f"\r[RMS] "
                        f"{event.get('value', 0.0):8.1f}",
                        end="",
                        flush=True)

                else:
                    print(f"\n[EVENT] {event}")

            except queue.Empty:
                continue

    except KeyboardInterrupt:
        shutdown_event.set()

    finally:
        print("\n\n[MAIN] Shutting down...")
        shutdown_event.set()

        capture_process.join(timeout=CAPTURE_SHUTDOWN_TIMEOUT)
        
        if capture_process.is_alive():
            print("[MAIN] Force stopping "
                "capture process")

            capture_process.terminate()
            capture_process.join(timeout=FORCE_TERMINATE_TIMEOUT)

        inference_process.join(timeout=INFERENCE_SHUTDOWN_TIMEOUT)

        if inference_process.is_alive():
            print("[MAIN] Force stopping "
                "inference process")

            inference_process.terminate()
            inference_process.join(timeout=FORCE_TERMINATE_TIMEOUT)

        transcript_process.join(timeout=TRANSCRIPT_SHUTDOWN_TIMEOUT)

        if transcript_process.is_alive():
            print("[MAIN] Force stopping "
                "transcript process")

            transcript_process.terminate()
            transcript_process.join(timeout=FORCE_TERMINATE_TIMEOUT)

        audio_queue.close()
        text_queue.close()
        status_queue.close()

        audio_queue.join_thread()
        text_queue.join_thread()
        status_queue.join_thread()

        print("[MAIN] Shutdown complete")


if __name__ == "__main__":

    multiprocessing.freeze_support()

    main()
