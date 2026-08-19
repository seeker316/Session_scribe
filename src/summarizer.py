from google import genai
from google.genai import types

from config import (
    GEMINI_MODEL_NAME,
    GEMINI_MAX_OUTPUT_TOKENS,
    GEMINI_SUMMARY_INSTRUCTION,
)

from logger import setup_logger

logger = setup_logger()


class SessionSummarizer:

    def __init__(self):
        self.client = genai.Client()

    def summarize(self, session):

        logger.info(
            "Starting summarization: %s_%s",
            session.name, session.session_id)

        transcript = self._read_transcript(session.transcript_file)

        if not transcript.strip():
            logger.warning("Transcript is empty: %s", session.transcript_file)
            return None

        response = self.client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=transcript,
            config=types.GenerateContentConfig(
                system_instruction=GEMINI_SUMMARY_INSTRUCTION,
                max_output_tokens=GEMINI_MAX_OUTPUT_TOKENS,
            )
        )

        summary = response.text.strip()
        summary_file = self._save_summary(session,summary)
        logger.info("Summary saved: %s",summary_file)

        return summary_file

    def _read_transcript(self, transcript_file):

        with open(transcript_file,"r", encoding="utf-8") as file:
            return file.read()

    def _save_summary(self, session, summary):
        with open(session.summary_file,"w", encoding="utf-8") as file:
            file.write(summary)
            file.write("\n")
        return session.summary_file

