from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane, Label, Static
from ui.screens.dashboard import DashboardScreen
from ui.screens.d1_manager import D1ManagerScreen
from ui.screens.r2_explorer import R2ExplorerScreen
from app.api_client import CloudflareClient
from app.query_history import get_query_history
from app.logger import log_info, log_error, log_warning
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
        self.query_history_manager = get_query_history()
        try:
            # Initialize client immediately in constructor
            self.client = CloudflareClient()
            log_info("CloudDash app initialized successfully")
        except ValueError as e:
            self.client = None
            log_error(f"Failed to initialize CloudflareClient: {e}")

    def on_mount(self) -> None:
        """Called when the app is first mounted."""
        if self.client:
            self.notify("✅ Connected to Cloudflare API", severity="information")
            log_info("Connected to Cloudflare API")
        else:
            self.notify("⚠️ Configuration Error: API keys missing in .env", severity="error", timeout=10)
            log_warning("Configuration Error: API keys missing in .env")

    def record_query(self, sql: str, rows_read: int, rows_returned: int, success: bool, 
                    database: str = "", table: str = "") -> None:
        """Record a query in history for the dashboard."""
        import datetime
        self.query_history_manager.add_query(
            sql=sql,
            rows_read=rows_read,
            rows_returned=rows_returned,
            success=success,
            database=database,
            table=table
        )
        
        # Update dashboard if it exists
        try:
            dashboard = self.query_one(DashboardScreen)
            if dashboard:
                dashboard.update_history(self.query_history_manager.get_history())
        except:
            pass

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
                yield Static("⚙️ CloudDash Settings", classes="section-title")
                
                # API Credentials Display
                yield Static("API Credentials Status", classes="sub-title")
                token = os.getenv("CLOUDFLARE_API_TOKEN", "Not Found")
                acc_id = os.getenv("CLOUDFLARE_ACCOUNT_ID", "Not Found")
                
                masked_token = f"{token[:4]}...{token[-4:]}" if token != "Not Found" and len(token) > 8 else ("Set" if token != "Not Found" else "❌ Not Set")
                masked_acc = f"{acc_id[:4]}...{acc_id[-4:]}" if acc_id != "Not Found" and len(acc_id) > 8 else ("Set" if acc_id != "Not Found" else "❌ Not Set")
                
                status_icon_token = "✅" if token != "Not Found" else "❌"
                status_icon_acc = "✅" if acc_id != "Not Found" else "❌"
                
                yield Static(f"{status_icon_token} API Token: [b cyan]{masked_token}[/]")
                yield Static(f"{status_icon_acc} Account ID: [b cyan]{masked_acc}[/]")
                
                # Connection Status
                yield Static("Connection Verification", classes="sub-title")
                if self.client:
                    yield Static("[b green]✅ Cloudflare client initialized successfully[/]")
                else:
                    yield Static("[b red]❌ Failed to initialize Cloudflare client[/]")
                
                # Query History Stats
                yield Static("Today's Query Statistics", classes="sub-title")
                stats = self.query_history_manager.get_today_stats()
                yield Static(f"Total Queries: [b]{stats['total_queries']}[/] (✅ {stats['successful']} | ❌ {stats['failed']})")
                yield Static(f"Total Row Reads: [b]{stats['total_row_reads']}[/]")
                yield Static(f"Avg Efficiency: [b cyan]{stats['avg_efficiency']:.1f}%[/]")
                
                # Help Text
                yield Static("", classes="sub-title")
                yield Static("[i]Note: If credentials are not set, create a .env file with:[/]")
                yield Static("[i]  CLOUDFLARE_API_TOKEN=your_token[/]")
                yield Static("[i]  CLOUDFLARE_ACCOUNT_ID=your_account_id[/]")
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark
