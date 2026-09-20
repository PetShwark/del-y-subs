from pathlib import Path
from pydantic import BaseModel
from textual import work
from textual.app import App, ComposeResult
from textual.screen import ModalScreen
from textual.containers import Container, Horizontal, Grid
from textual.widgets import Header, Footer, DataTable, Label, Button
from .youtube_subs import YouTubeSubscriptions, YouTubeSubscriptionInfo
from . import constants


class DelYSubsDataTableRow(BaseModel):
    selected: bool
    channel_id: str
    channel_name: str
    channel_descr: str


class YesNoDialog(ModalScreen[bool]):
    """A modal screen with Yes and No buttons."""

    CSS_PATH = "yes_no_dialog.tcss"

    def __init__(self, message1: str, message2: str) -> None:
        super().__init__()
        self.message1 = message1
        self.message2 = message2
    
    def compose(self) -> ComposeResult:
        with Grid(id="dialog-window"):
            yield Label(self.message1, id="message1")
            yield Label(self.message2, id="message2")
            yield Button("Yes", id="yes", variant="success")
            yield Button("No", id="no", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.dismiss(True)
        else:
            self.dismiss(False)


class DelYSubsApp(App):
    """A simple Textual TUI application."""

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit_app", "Quit app"),
        ("x", "unsubscribe_selected", "Unsubscribe selected channels"),
    ]
    CSS_PATH = "app.tcss"
    TITLE = "Del-YouTube-Subs"

    def __init__(self, client_secrets_file_path: Path, token_file_path: Path):
        super().__init__()
        self.confirm = False
        self.client_secrets_file = client_secrets_file_path
        self.token_file = token_file_path 
        self.youtube_subs = YouTubeSubscriptions(
            token_file=self.token_file, 
            secrets_file=self.client_secrets_file
        )
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        dt = self.query_one(DataTable)
        dt.border_title = "Your YouTube Subscriptions"
        dt.cursor_type = "row"
        dt.zebra_stripes = True
        self.selected_col_key = dt.add_column("Selected", width=8)
        self.channel_col_key = dt.add_column("YouTube Channel", width=32)
        self.description_col_key = dt.add_column("Description")
        dt.loading = True
        self.get_youtube_subs_data()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        dt = event.data_table
        row_key = event.row_key
        current_selection = dt.get_cell(row_key, self.selected_col_key)
        dt.update_cell(row_key, self.selected_col_key, f"   {toggle_selection_char(current_selection)}")
        dt.refresh_row(event.cursor_row)

    def action_quit_app(self) -> None:
        self.exit()

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )    

    def check_confirm_unsubscribe_selected(self, confirmed: bool | None) -> None:
        if confirmed:
            self.do_unsubscribe_selected()
        else:
            self.notify("Action cancelled.", severity="error")

    def action_unsubscribe_selected(self) -> None:
        # Obtain confirmation
        selected_subscription_names = ", ".join(map(lambda x: x.channel_name, self.get_selected_subscriptions()))
        self.push_screen(
            YesNoDialog(
                f"You have selected {selected_subscription_names} for unsubscribing.",
                "Are you sure? Unsubscribing is not reversible."
            ),
            self.check_confirm_unsubscribe_selected)

    def get_selected_subscriptions(self) -> list[YouTubeSubscriptionInfo]:
        result: list[YouTubeSubscriptionInfo] = []
        dt = self.query_one(DataTable)
        for row_key in dt.rows.keys(): #Row keys are the subscription IDs from YouTube API
            selected_val = str(dt.get_cell(row_key, self.selected_col_key)).strip() #Value is padded with spaces
            if selected_val == constants.SELECTION_CHAR:
                result.append(
                    YouTubeSubscriptionInfo(
                        channel_ID=str(row_key.value),
                        channel_name=str(dt.get_cell(row_key,self.channel_col_key)).strip(),
                        channel_descr=str(dt.get_cell(row_key,self.description_col_key)).strip()
                    )
                )
        return result
                
    @work(thread=True)
    async def do_unsubscribe_selected(self) -> None:
        selected_subscriptions = self.get_selected_subscriptions()
        for subscription in selected_subscriptions:
            success = await self.youtube_subs.unsubscribe_from_channel(subscription.channel_ID)
        self.get_youtube_subs_data() #Re-load DataTable after unsubscribing
        

    @work(thread=True)
    async def get_youtube_subs_data(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        youtube_subs_data = await self.youtube_subs.get_subscriptions()
        for subscription in list(sorted(youtube_subs_data, key=lambda x: x.channel_name.lower())):
            data_table_row = [
                f"   {constants.DESELECTION_CHAR}",
                subscription.channel_name,
                subscription.channel_descr
            ]
            self.call_from_thread(table.add_row, *data_table_row, key=subscription.channel_ID)
        self.call_from_thread(setattr, table, "loading", False)


def toggle_selection_char(selection_char: str) -> str:
    return constants.DESELECTION_CHAR if constants.SELECTION_CHAR in selection_char else constants.SELECTION_CHAR