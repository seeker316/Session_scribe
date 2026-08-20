from session_manager import SessionManager

from tui import SessionSelector

from main import main


def main_tui():

    manager = SessionManager()

    app = SessionSelector(manager, status_queue)

    session = app.run()

    if session is None:
        return

    print(
        f"\nStarting session: "
        f"{session.name}_{session.session_id}"
    )

    main(session)


if __name__ == "__main__":
    main_tui()
