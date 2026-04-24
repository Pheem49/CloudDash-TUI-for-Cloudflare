from textual.app import ComposeResult
from textual.widgets import Static, DataTable
from textual.containers import Vertical, Horizontal
from textual.screen import Screen

class DashboardScreen(Static):
    """The main dashboard showing Row-Read Monitor and recent activity."""

    def update_history(self, history: list) -> None:
        """Update the history table with new data."""
        table = self.query_one("#query-history-table", DataTable)
        table.clear()
        
        for entry in history:
            rows_read = entry["rows_read"]
            # Color coding for Row Reads
            color = "green"
            if rows_read > 1000: color = "yellow"
            if rows_read > 10000: color = "red"
            
            row_read_styled = f"[{color}]{rows_read}[/]"
            table.add_row(entry["time"], entry["sql"], row_read_styled, entry["status"])

    def compose(self) -> ComposeResult:
        yield Static("Live Row-Read Monitor", classes="section-title")
        with Vertical(id="monitor-container"):
            yield Static("Recent Queries Performance", classes="sub-title")
            table = DataTable(id="query-history-table")
            table.add_columns("Time", "Query", "Row Reads", "Status")
            yield table
        
        with Horizontal(id="stats-summary"):
            yield Static("Total Reads (24h): 0", classes="stat-box")
            yield Static("Avg Rows/Query: 0", classes="stat-box")
            yield Static("Efficiency: 100%", classes="stat-box")
