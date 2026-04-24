from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane, Label, Static
from ui.screens.dashboard import DashboardScreen
from ui.screens.d1_manager import D1ManagerScreen
from ui.screens.r2_explorer import R2ExplorerScreen
from app.api_client import CloudflareClient
import os
from dotenv import load_dotenv

load_dotenv()

class CloudDashApp(App):
    """CloudDash: A terminal UI to manage Cloudflare D1 and R2."""

    CSS_PATH = "style.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.query_history = []
        try:
            # Initialize client immediately in constructor
            self.client = CloudflareClient()
        except ValueError:
            self.client = None

    def on_mount(self) -> None:
        """Called when the app is first mounted."""
        if self.client:
            self.notify("Connected to Cloudflare API", severity="information")
        else:
            self.notify("Configuration Error: API keys missing in .env", severity="error", timeout=10)

    def record_query(self, sql: str, rows_read: int, success: bool) -> None:
        """Record a query in history for the dashboard."""
        import datetime
        entry = {
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "sql": sql,
            "rows_read": rows_read,
            "status": "Success" if success else "Error"
        }
        self.query_history.insert(0, entry)
        # Update dashboard if it exists
        dashboard = self.query_one(DashboardScreen)
        if dashboard:
            dashboard.update_history(self.query_history)

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with TabbedContent(initial="dashboard"):
            with TabPane("Dashboard", id="dashboard"):
                yield DashboardScreen()
            with TabPane("D1 (Database)", id="d1"):
                yield D1ManagerScreen()
            with TabPane("R2 (Storage)", id="r2"):
                yield R2ExplorerScreen()
            with TabPane("Settings", id="settings"):
                yield Static("Configuration", classes="section-title")
                
                # Get masked values for display
                token = os.getenv("CLOUDFLARE_API_TOKEN", "Not Found")
                acc_id = os.getenv("CLOUDFLARE_ACCOUNT_ID", "Not Found")
                
                masked_token = f"{token[:4]}...{token[-4:]}" if token != "Not Found" else token
                masked_acc = f"{acc_id[:4]}...{acc_id[-4:]}" if acc_id != "Not Found" else acc_id
                
                yield Static(f"API Token: [b]{masked_token}[/b]")
                yield Static(f"Account ID: [b]{masked_acc}[/b]")
                yield Static("\n[i]Note: If values are 'Not Found', please check your .env file and restart the app.[/i]")
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark
