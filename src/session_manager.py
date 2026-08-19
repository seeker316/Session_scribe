import json
import os
import re
import secrets

from dataclasses import dataclass
from datetime import datetime

from config import SESSIONS_DIR
from logger import setup_logger

logger = setup_logger()

@dataclass
class Session:
    name: str
    session_id: str
    start_time: datetime
    last_active: datetime

    directory: str
    transcript_file: str
    metadata_file: str
    summary_file: str

class SessionManager:
    def __init__(self, sessions_dir=SESSIONS_DIR):
        self.sessions_dir = sessions_dir

    @staticmethod
    def _sanitize_name(name):
        name = name.replace(" ", "_")
        name = re.sub(r"[^a-zA-Z0-9_-]","",name)
        return name

    def create_session(self, name):
        name = name.strip()
        if not name:
            raise ValueError("Session name cannot be empty")

        name = self._sanitize_name(name)
        session_id = secrets.token_hex(2)
        now = datetime.now()

        date_directory = now.strftime("%Y-%m-%d")
        date_path = os.path.join(self.sessions_dir,date_directory)

        base_name = (f"{name}_{session_id}")
        
        directory = os.path.join(date_path, base_name)
        os.makedirs(directory,exist_ok=True)
        
        transcript_file = os.path.join(directory, "transcript.txt")
        metadata_file = os.path.join(directory, "metadata.json")
        summary_file = os.path.join(directory,"summary.md")
        
        session = Session(
            name=name,
            session_id=session_id,
            start_time=now,
            last_active=now,
            directory=directory,
            transcript_file=transcript_file,
            metadata_file=metadata_file,
            summary_file=summary_file
            )

        with open(transcript_file, "w", encoding="utf-8") as file:
            file.write("=" * 60 +"\n")
            file.write(f"Session: {session.name}\n")
            file.write(f"ID: {session.session_id}\n")
            file.write(f"Started: "
                       f"{session.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            file.write("=" * 60 +"\n\n")
        
        self._save_metadata(session)
        logger.info(
            "Session created: %s_%s",
            session.name,
            session.session_id
        )

        return session

    def list_sessions(self):

        sessions = []

        if not os.path.exists(self.sessions_dir):
            return sessions

        for date_directory in os.listdir(self.sessions_dir):

            date_path = os.path.join(
                self.sessions_dir,
                date_directory
            )

            if not os.path.isdir(date_path):
                continue

            for session_directory in os.listdir(date_path):

                session_path = os.path.join(
                    date_path,
                    session_directory
                )

                if not os.path.isdir(session_path):
                    continue

                metadata_file = os.path.join(
                    session_path,
                    "metadata.json"
                )

                if not os.path.isfile(metadata_file):
                    continue

                try:

                    session = self._load_metadata(
                        metadata_file
                    )

                    sessions.append(session)

                except (
                    OSError,
                    json.JSONDecodeError,
                    KeyError,
                    ValueError
                ) as error:

                    logger.warning(
                        "Failed to load session "
                        "metadata '%s': %s",
                        metadata_file,
                        error
                    )

                    continue

        sessions.sort(
            key=lambda session: session.last_active,
            reverse=True
        )

        return sessions

    def load_session(self, session_id):
        sessions = self.list_sessions()
        for session in sessions:
            if session.session_id == session_id:
                logger.info(
                    "Session loaded: %s_%s",
                    session.name,
                    session.session_id
                )
                return session
            
        raise ValueError(f"Session '{session_id}' not found.")


    def update_last_active(self, session):
        session.last_active = datetime.now()
        self._save_metadata(session)


    def _save_metadata(self, session):
        metadata = {
            "name": session.name,
            "session_id": session.session_id,
            "start_time": session.start_time.isoformat(),
            "last_active": session.last_active.isoformat(),
            "directory": session.directory,
            "transcript_file": session.transcript_file,
            "metadata_file": session.metadata_file,
            "summary_file": session.summary_file
        }

        with open(session.metadata_file,"w", encoding="utf-8") as file:
            json.dump(metadata, file, indent=4)


    def _load_metadata(self, metadata_file):
        with open(metadata_file, "r", encoding="utf-8") as file:
            metadata = json.load(file)

        return Session(
            name=metadata["name"],
            session_id= metadata["session_id"],
            start_time= datetime.fromisoformat(metadata["start_time"]),
            last_active= datetime.fromisoformat(metadata["last_active"]),
            directory= metadata["directory"],
            transcript_file= metadata["transcript_file"],
            metadata_file= metadata["metadata_file"],
            summary_file=metadata["summary_file"])


   

