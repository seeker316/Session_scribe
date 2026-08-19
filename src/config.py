#config.py
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
SESSIONS_DIR = DATA_DIR / "sessions"

INPUT_SAMPLE_RATE = 48000
OUTPUT_SAMPLE_RATE = 16000

AUDIO_CHANNELS = 1
AUDIO_CHUNK_SIZE = 1024
AUDIO_DEVICE_INDEX = 0

AUDIO_SEGMENT_ENERGY_THRESHOLD = 6000
AUDIO_SEGMENT_SILENCE_DURATION = 2.5

RMS_UPDATE_INTERVAL = 0.1

WHISPER_MODEL_NAME = "medium"
WHISPER_LANGUAGE = "en"

AUDIO_QUEUE_SIZE = 10
TEXT_QUEUE_SIZE = 20
STATUS_QUEUE_SIZE = 100

CAPTURE_SHUTDOWN_TIMEOUT = 2
INFERENCE_SHUTDOWN_TIMEOUT = 20
TRANSCRIPT_SHUTDOWN_TIMEOUT = 5
FORCE_TERMINATE_TIMEOUT = 5

TUI_POLL_INTERVAL = 0.1

# Gemini
GEMINI_MODEL_NAME = "gemini-3.5-flash-lite"

GEMINI_MAX_OUTPUT_TOKENS = 1000

GEMINI_SUMMARY_INSTRUCTION = """
You are summarizing a recorded work session.

Create a concise but useful summary of the session.

Do not invent information that is not present in the transcript.

Use exactly this structure:

# Session Summary

## Overview

Give a short overview of what the session was about.

## Key Topics

List the main topics discussed.

## Important Decisions

List decisions or conclusions that were actually made.

## Problems / Issues

List problems, bugs, questions, or uncertainties mentioned.

## Next Steps

List explicit or strongly implied next actions.
"""
