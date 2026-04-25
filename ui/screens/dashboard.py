from textual.app import ComposeResult
from textual.widgets import Static, DataTable
from textual.containers import Vertical, Horizontal
from textual.screen import Screen

class DashboardScreen(Static):
    """The main dashboard showing Row-Read Monitor and recent activity."""

    def update_history(self, history: list) -> None:
        """Update the history table and stats boxes with new data."""
        table = self.query_one("#query-history-table", DataTable)
        table.clear()
        
        total_reads = 0
        total_returned = 0
        success_queries = 0
        
        for entry in history:
            rows_read = entry["rows_read"]
            rows_returned = entry.get("rows_returned", 0)
            
            if entry["status"] == "Success":
                total_reads += rows_read
                total_returned += rows_returned
                success_queries += 1
            
            # Color coding for Row Reads
            color = "green"
            if rows_read > 1000: color = "yellow"
            if rows_read > 10000: color = "red"
            
            row_read_styled = f"[{color}]{rows_read}[/]"
            table.add_row(entry["time"], entry["sql"], row_read_styled, entry["status"])

        # Update stats boxes
        if success_queries > 0:
            avg_reads = total_reads / success_queries
            efficiency = (total_returned / total_reads * 100) if total_reads > 0 else 100
            if efficiency > 100: efficiency = 100 # Cap at 100%
            
            self.query_one("#stat-total").update(f"Total Reads (24h): [b]{total_reads}[/]")
            self.query_one("#stat-avg").update(f"Avg Rows/Query: [b]{avg_reads:.1f}[/]")
            
            eff_color = "green"
            if efficiency < 50: eff_color = "yellow"
            if efficiency < 10: eff_color = "red"
            self.query_one("#stat-efficiency").update(f"Efficiency: [{eff_color}][b]{efficiency:.1f}%[/][/]")

    def compose(self) -> ComposeResult:
        yield Static("Live Row-Read Monitor", classes="section-title")
        with Vertical(id="monitor-container"):
            yield Static("Recent Queries Performance", classes="sub-title")
            table = DataTable(id="query-history-table")
            table.add_columns("Time", "Query", "Row Reads", "Status")
            yield table
        
        with Horizontal(id="stats-summary"):
            yield Static("Total Reads (24h): 0", classes="stat-box", id="stat-total")
            yield Static("Avg Rows/Query: 0", classes="stat-box", id="stat-avg")
            yield Static("Efficiency: 100%", classes="stat-box", id="stat-efficiency")
