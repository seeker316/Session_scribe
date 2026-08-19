- creates the session dir, for each date. 
- opens if a session already exists, or else creates a new session, with input name and a random_hex_token.
- creates transcript file and the meta data file containing the following information.
```
    name: str
    session_id: str
    start_time: datetime
    last_active: datetime

    directory: str
    transcript_file: str
    metadata_file: str
```

- has methods to create_sessions, load and list_sessions,
- has methods to view and edit metadata, like load_metadata and save_metadata.