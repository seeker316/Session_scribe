from session_manager import SessionManager
from summarizer import SessionSummarizer

session_manager = SessionManager()

sessions = session_manager.list_sessions()

if not sessions:
    print("No sessions found.")
    exit()

session = sessions[0]

print(
    f"Summarizing: "
    f"{session.name}_{session.session_id}"
)

summarizer = SessionSummarizer()

summary_file = summarizer.summarize(
    session
)

print(
    f"Summary saved to: {summary_file}"
)

