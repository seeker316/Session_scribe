Contains classes containing the ui and configuration binding for all the windows, like select session create session and other stuff.

```
App → your main Textual application.
Screen → individual UI screens.
ListView → selectable list.
ListItem → one item inside the list.
Input → text input.
Button → buttons.
Label / Static → display text.
```

- Session Item : represents one existing session in the ListView, here we are attaching actual object to the UI item

- New session Screen : UI for creating a new session, seperate textual screen that appears when the user selects, NewSessionScreen
	- The constructor recieves an existing session_manager, because it creates a new session.
	- the compose function is a textual way of saying build the widgets that belong on this screen.
	- `on_mount` is a textual liufecycle callback, when the screen is mounted, it accepts the input from user and uses a text handler, `on_input_submitted` which is called when the user presses enter.
	- `on_button_pressed` are button callbacks.

> yield: turns a normal python function into a generator, `return ` gives you a value and ends the function. `yield` gives you a value and pauses the function.

- SessionSelector : Shows existing sessions and allows user to select or create one.
	- constructor requires session_manager, status queue for debug info and `on_session_selected`, which points to the selected session from the main.
	- `compose` : creates list of existing sessions and creates "+ New Session", turns every actual session object into a UI SessionItem. When the user selects an item and the selected item is an existing session it calls `select_session()`.
		if the item isn't Session Item then it is +NewSession, it'll open NewSessionScreen and call  [[session_manager | new_session_created]], which creates a bew session and then also selects the newly created session using `select_session().
	
	- `select_Session()` acts like a bridge it returns the selected session and calls the `on_session_selected` from [[SessionScribe (Main.py)| main]] , which then starts all the other processes. and pushes `LiveSessionScreen`, with selected session.

- LiveSessionScreen : recording / live transcription UI.
	- constructor requires session to know which session is running and status_queue. `Appstate` is used to store things in a application state rather than putting it directly on the ui.
	- `compose` : retrieves current session, retrieves current status of the program and displays that .
	- `poll_events` : the `on_mount` function has an set_interval which calls `poll_events` function every 0.1 seconds/ `poll_events` retrieves the latest item from status queue without blocking it. Once the event is recieved, The state changes and `refresh_ui`, updates the visible UI.

- `action_quit_app` : exits the entire textual application,
- `action_back` : removes the current screen and goes back to the previous one.

> BINDINGS = [
> ("escape", "cancel", "Cancel"),], keyboard bindings, pressing escape closes the screen and returns none, it calls action_cancel.



