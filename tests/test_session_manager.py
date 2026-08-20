from session_manager import SessionManager

def main():

    manager = SessionManager()

    print("\nCreating session...\n")

    session = manager.create_session()

    print("\nCreated:")
    print(
        f"  Name:        {session.name}"
    )
    print(
        f"  ID:          {session.session_id}"
    )
    print(
        f"  Started:     {session.start_time}"
    )
    print(
        f"  Last active: {session.last_active}"
    )
    print(
        f"  Transcript:  {session.transcript_file}"
    )

    print("\nExisting sessions:\n")

    sessions = manager.list_sessions()

    for session in sessions:

        print(
            f"{session.session_id} | "
            f"{session.name} | "
            f"{session.last_active}"
        )

    print("\nLoading first session...\n")

    session = manager.load_session(
        sessions[0].session_id
    )

    print(
        f"Resumed: {session.name}"
    )

    print(
        f"Transcript: {session.transcript_file}"
    )

    print(
    "\nUpdating last active...")

    manager.update_last_active(
        session
    )

    print(
        session.last_active
    )


if __name__ == "__main__":
    main()
