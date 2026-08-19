import queue
import time
from dataclasses import dataclass, field
import threading

from textual.app import App, ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
    RichLog
)

from session_manager import SessionManager
from config import TUI_POLL_INTERVAL

@dataclass
class AppState:

    session: object
    status: str = "Starting..."
    recording: bool = False
    rms: float = 0.0
    paused: bool = False
    inference_active: bool = False
    audio_duration: float = 0.0
    inference_time: float = 0.0

    transcript: list[str] = field(
        default_factory=list
    )

class SessionItem(ListItem):

    def __init__(self, session):

        self.session = session

        super().__init__(
            Label(
                f"{session.name}_{session.session_id}"
            )
        )

class NewSessionScreen(Screen):

    CSS = """
    #new-session-container {
        width: 60%;
        height: auto;
        border: round $accent;
        padding: 2 4;
        align: center middle;
    }

    #title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        margin-bottom: 2;
    }

    #session-input {
        width: 100%;
        margin-bottom: 2;
    }

    #buttons {
        width: 100%;
        height: auto;
        align: center middle;
    }

    Button {
        margin: 0 1;
    }

    #error {
        width: 100%;
        height: auto;
        color: $error;
        content-align: center middle;
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, session_manager):
        super().__init__()
        self.session_manager = session_manager

    def compose(self) -> ComposeResult:
        with Container(id="new-session-container"):
            yield Label("New Session", id="title")
            yield Label("Session name:")
            yield Input(placeholder="e.g. nav2 debugging", id="session-input")
            yield Label("", id="error")

            with Container(id="buttons"):
                yield Button("Create", variant="primary", id="create")
                yield Button("Cancel", id="cancel")

    def on_mount(self):
        self.query_one("#session-input",Input).focus()

    def on_input_submitted(self,event: Input.Submitted):
        self.create_session()

    def on_button_pressed(self,event: Button.Pressed):
        if event.button.id == "create":
            self.create_session()
        elif event.button.id == "cancel":
            self.dismiss(None)

    def create_session(self):
        input_widget = self.query_one("#session-input",Input)

        name = input_widget.value.strip()
        if not name:
            self.query_one("#error",Label).update("Session name cannot be empty.")
            input_widget.focus()
            return

        session = (self.session_manager.create_session(name))
        self.dismiss(session)


    def action_cancel(self):
        self.dismiss(None)



class SessionSelector(App):

    TITLE = "SESSION SCRIBE"

    CSS = """
    Screen {
        align: center middle;
    }

    #container {
        width: 80%;
        height: 80%;
        border: round $accent;
    }

    #title {
        height: 3;
        content-align: center middle;
        text-style: bold;
    }

    #sessions {
        height: 1fr;
    }

    #hint {
        height: 3;
        content-align: center middle;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
    ]

    def __init__(self, session_manager,on_session_selected):
        super().__init__()
        self.session_manager = session_manager
        self.on_session_selected = on_session_selected

    def compose(self) -> ComposeResult:
        sessions = self.session_manager.list_sessions()
        items = [ListItem(Label("+ New Session"))]

        for session in sessions:
            items.append(SessionItem(session))

        with Container(id="container"):
            yield Label("SESSION SCRIBE", id="title")
            yield ListView(*items, id="sessions")
            yield Label("↑ ↓ Navigate    Enter Select    Q Quit", id="hint")
        yield Footer()

    def on_mount(self):
        self.query_one("#sessions",ListView).focus()

    def on_key(self, event):
        if event.key == "q":
            self.action_quit()
            event.stop()

        elif event.key == "escape":
            self.action_quit()
            event.stop()

    def on_list_view_selected(self, event: ListView.Selected):
        item = event.item
        if isinstance(item, SessionItem):
            self.select_session(item.session)
            return
        time.sleep(0.5)
        self.push_screen(NewSessionScreen(self.session_manager),self.new_session_created)

 
    def new_session_created(self, session):
        if session is not None:
            self.select_session(session)
        
    def select_session(self, session):
        status_queue, on_exit, on_pause, on_resume = self.on_session_selected(session)
        time.sleep(0.5)
        self.push_screen(LiveSessionScreen(session, status_queue, on_exit, on_pause, on_resume))
       

class LiveSessionScreen(Screen):

    CSS = """
    #live-container {
        width: 95%;
        height: 95%;
        border: round $accent;
        align-horizontal: center;
    }
    
    #title {
        width: 1fr;
        height: 2;
        content-align: center middle;
        text-align: center;
        text-style: bold;
    }

    #session-info {
        height: 4;
        padding: 1 2;
    }

    #transcript-title {
        height: 2;
        padding: 0 2;
        text-style: bold;
    }

    #transcript {
        height: 1fr;
        padding: 1 2;
        overflow-y: auto;
    }

    #status {
        height: 6;
        padding: 1 2;
        border-top: solid $accent;
    }

    #controls {
        height: 3;
        content-align: center middle;
        border-top: solid $accent;
    }
    """

    BINDINGS = [
        ("space", "toggle_pause", "Pause"),
        ("q", "quit_app", "Quit"),
        ("escape", "back", "Back"),
    ]

    def __init__(self, session, status_queue, on_exit, on_pause, on_resume):
        super().__init__()
        self.status_queue = status_queue
        self.state = AppState(session=session)
        self.on_exit = on_exit
        self.on_pause = on_pause
        self.on_resume = on_resume
        self.finalizing = False

    def compose(self) -> ComposeResult:
        with Container(id="live-container"):

            yield Label("SESSION SCRIBE",id="title")

            yield Static(self.session_text(), id="session-info")

            yield Label("TRANSCRIPT", id="transcript-title")

            yield RichLog(id="transcript", 
                            highlight=True, markup=True, wrap=True)

            yield Static(self.status_text(), id="status")

            yield Static(
                "SPACE (Pause)     "
                "ESC (Sessions)    "
                "Q (Quit)",
                id="controls"
            )

        yield Footer()

    def session_text(self):
        session = self.state.session
        return (
            f"Session: "
            f"{session.name}_{session.session_id}\n"
            f"Started: "
            f"{session.start_time.strftime('%H:%M:%S')}"
        )

    def status_text(self):
        recording = (
            "● RECORDING"
            if self.state.recording
            else "○ STOPPED"
        )

        inference = (
            "PROCESSING"
            if self.state.inference_active
            else "IDLE"
        )

        return (
            f"{recording} | Whisper: {inference}"
            f" | STATUS: {self.state.status}\n" 
            f"Audio: {self.state.audio_duration:.2f}s    "
            f"Inference: "
            f"{self.state.inference_time:.2f}s\n"
            f"RMS: {self.rms_bar()} | [{self.state.rms:.0f}]\n"
        )

    def rms_bar(self, width=35):
        max_rms = 32767.0
        level = min(self.state.rms / max_rms, 1.0)
        filled = int(level * width)
        
        return ("█" * filled+ "░" * (width - filled))
    

    def on_mount(self):
        self.poll_timer = self.set_interval(TUI_POLL_INTERVAL, self.poll_events)
    
    def poll_events(self):
        while True:
            try:
                event = self.status_queue.get_nowait()
            except queue.Empty:
                break
            except ValueError:
                break

            self.handle_event(event)

    def refresh_ui(self):
        self.query_one("#session-info",Static).update(self.session_text())
        self.query_one("#status",Static).update(self.status_text())

    def handle_event(self, event):
        event_type = event.get("type")

        if event_type == "capture_started":
            self.state.recording = True
            self.state.status = "Listening..."
        
        elif event_type == "rms":
            self.state.rms = event.get("value",0.0)

        elif event_type == "capture_stopped":
            self.state.recording = False
            self.state.status = "Capture stopped"

        elif event_type == "segment_created":
            self.state.audio_duration = (
                event.get("duration", 0.0))
            
            self.state.status = "Audio segment ready"

        elif event_type == "inference_started":
            self.state.inference_active = True
            
            self.state.status = "Transcribing..."
            self.state.audio_duration = (event.get("audio_duration", self.state.audio_duration))

        elif event_type == "inference_completed":
            self.state.inference_active = False

            if not self.state.paused:
                self.state.status = "Transcription complete"

            self.state.inference_time = event.get("inference_time", 0.0)
            text = event.get("text", "").strip()

            if text:
                self.state.transcript.append(text)
                transcript_widget = self.query_one(
                    "#transcript", RichLog)
                transcript_widget.write(text)

        elif event_type == "transcript_saved":
            if not self.state.paused:
                self.state.status = "Listening..."

        self.refresh_ui()

    def action_toggle_pause(self):
        if self.finalizing:
            return
        if self.state.paused:
            self.on_resume()
            self.state.paused = False
            self.state.status = "Listening..."

        else:
            self.on_pause()
            self.state.paused = True
            self.state.status = "Paused"

        self.refresh_ui()

    def action_back(self):
        if self.finalizing:
            return
        self.poll_timer.pause()
        
        self.finalizing = True
        self.state.status = "Ending session..."
        self.refresh_ui()
        threading.Thread(target=self.on_exit, args=(self.set_finalization_status,), daemon=True).start()


    def set_finalization_status(self, status):
        self.app.call_from_thread(self._update_finalization_status, status)


    def _update_finalization_status(self, status):
        self.state.status = status
        self.refresh_ui()

        if status == "Summary saved":
            self.app.pop_screen()

    def action_quit_app(self):
        if self.finalizing:
            return

        self.finalizing = True
        self.poll_timer.pause()
        self.state.status = "Ending session..."
        self.refresh_ui()

        threading.Thread(target=self.on_exit, args=(self.set_finalization_status,),daemon=True).start()

