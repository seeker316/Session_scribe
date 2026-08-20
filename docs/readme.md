# SESSION_SCRIBE
A local speech-to-text tool for recording work sessions, transcribing them with Whisper, and automatically generating a concise session summary using Gemini.

The application provides a Textual-based terminal UI for managing sessions and monitoring:

- Live audio capture
- RMS audio level
- Speech segmentation
- Whisper transcription
- Live transcript
- Pause / resume
- Session persistence
- Automatic session summarization
- Structured session logs

---
## Features

### Audio Capture

Captures microphone audio at:
- Sample rate: 48 kHz
- Channels: 1
- Sample format: 16-bit PCM
Audio is processed in chunks and passed to the speech segmenter.

### Speech Segmentation

The `AudioSegmenter` calculates RMS energy and detects speech based on an energy threshold.

Detected speech is accumulated until sufficient silence is observed.

### Audio Resampling

Speech segments are resampled from:

```text
48 kHz → 16 kHz
```


### Transcription

OpenAI Whisper is used locally for speech-to-text transcription.
The current configuration uses: `medium`
The transcription pipeline can use CUDA when available.

### Session Management

Each session gets its own directory:
```
data/
└── sessions/
    └── YYYY-MM-DD/
        └── session_name_id/
            ├── transcript.txt
            ├── metadata.json
            └── summary.md
```

### Automatic Summarization

When a session is closed:
1. The audio pipeline shuts down.
2. The transcript is finalized.
3. Gemini summarizes the complete transcript.
4. `summary.md` is generated.
5. The application returns to the session selector.

---
# Requirements

- Linux
- Python 3.12+
- PortAudio
- A working microphone
- Gemini API key
- CUDA is optional
---

# System Dependencies

The application uses PyAudio, which requires PortAudio.

On Ubuntu/Debian:
```
sudo apt update
sudo apt install portaudio19-dev python3-dev
```

If PyAudio installation fails, install the system dependencies first and then run:
```
pip install pyaudio
```


---
# Installation

Clone the repository:

```
git clone https://github.com/seeker316/Session_scribe.git
```

Create a virtual environment and activate it:
```
python3 -m venv .venv
source .venv/bin/activate
```

Install the project:
```
pip install -e .
```

---

# Gemini API Key

The summarizer uses Google's Gemini API.

Create a Gemini API key and set it as an environment variable:
```
export GEMINI_API_KEY="your_api_key_here"
```

For persistent configuration, add the export to your shell configuration:
```
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.bashrc

source ~/.bashrc

echo $GEMINI_API_KEY
```

---

# Configuration

Project configuration is stored in:
```
src/config.py
```

Configuration includes things such as:
- Audio settings
- Queue sizes
- Shutdown timeouts
- Whisper model
- Gemini model
- Gemini summarization instructions
- Session storage location

Modify these values instead of hardcoding them throughout the application.

---

# Running

```
python3 src/main.py
```

The terminal UI provides:
- New Session
- Existing Sessions

Select a session to start recording.

---

# Controls

Inside a live session:
```
SPACE    Pause / Resume

ESC      End session / Return to sessions

Q        Quit
```

The live UI displays:

- Recording state
- Current status
- RMS audio level
- Whisper processing state
- Audio duration
- Inference time
- Live transcript

---
