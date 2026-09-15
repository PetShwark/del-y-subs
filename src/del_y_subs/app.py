from textual import events
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DataTable, Log

class DelYSubsApp(App):
    """A simple Textual TUI application."""
    
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit_app", "Quit app")
    ]
    CSS_PATH = "app.tcss"

    def setup_datatable(self) -> None:
        self.dt.add_columns(("Selected", "selected"),
                            ("YouTube Channel", "channel"),
                            ("Description", "description"))
        self.dt.add_row("X", "Channel 1", "Description of Channel 1", key="channelID001")
        self.dt.add_row("X", "Channel 2", "Description of Channel 2", key="channelID002")
        self.dt.add_row("X", "Channel 3", "Description of Channel 3", key="channelID003")
        self.dt.add_row("X", "Channel 4", "Description of Channel 4", key="channelID004")
        self.dt.add_row("X", "Channel 5", "Description of Channel 5", key="channelID005")
        self.dt.add_row("X", "Channel 6", "Description of Channel 6", key="channelID006")
        self.dt.add_row("X", "Channel 7", "Description of Channel 7", key="channelID007")
        self.dt.add_row("X", "Channel 8", "Description of Channel 8", key="channelID008")
        self.dt.add_row("X", "Channel 9", "Description of Channel 9", key="channelID009")
        self.dt.add_row("X", "Channel 10", "Description of Channel 10", key="channelID010")

    def compose(self) -> ComposeResult:
        self.dt = DataTable(id="subs_data_table")
        self.dt.border_title = "Your YouTube Subscriptions"
        self.dt.cursor_type = "row"
        self.setup_datatable()
        yield Header()
        yield self.dt
        yield Footer()

    def action_quit_app(self) -> None:
        self.exit()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

