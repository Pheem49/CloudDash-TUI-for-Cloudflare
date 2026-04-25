from textual.app import ComposeResult
from textual.widgets import Static, ListView, ListItem, Label, Input, Button, DataTable
from textual.containers import Horizontal, Vertical, Grid
from textual.screen import Screen

class D1ManagerScreen(Static):
    """Screen for managing D1 databases and running queries."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_db_id = None
        self.table_row_counts = {}
        self.analysis_timer = None

    async def on_mount(self) -> None:
        """Fetch databases when the screen is mounted."""
        import asyncio
        await asyncio.sleep(0.5)  # Wait for app.client to be ready
        await self.refresh_databases()

    async def refresh_databases(self) -> None:
        """Fetch and display D1 databases."""
        if not hasattr(self.app, 'client') or not self.app.client:
            self.app.notify("Cloudflare Client not initialized", severity="error")
            return

        db_list = self.query_one("#database-list", ListView)
        db_list.clear()
        
        try:
            databases = await self.app.client.list_d1_databases()
            if not databases:
                self.app.notify("No D1 databases found in this account.", severity="warning")
            
            for db in databases:
                db_list.append(ListItem(Label(db["name"]), id=f"db-{db['uuid']}"))
            
            self.query_one("#d1-main-content Label").update(f"Select a database to start")
        except Exception as e:
            self.app.notify(f"Error fetching D1: {e}", severity="error")

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle selection of a database or table."""
        if event.list_view.id == "database-list":
            db_id = event.item.id.replace("db-", "")
            db_name = str(event.item.query_one(Label).renderable)
            await self.select_database(db_id, db_name)
        elif event.list_view.id == "table-list":
            table_name = str(event.item.query_one(Label).renderable)
            await self.show_table_schema(table_name)

    async def show_table_schema(self, table_name: str) -> None:
        """Fetch and display schema for the selected table."""
        try:
            # Wrap table name in double quotes to handle special characters like _cf_KV
            res = await self.app.client.query_d1(self.selected_db_id, f'PRAGMA table_info("{table_name}")')
            if res.get("success"):
                rows = res["result"][0].get("results", [])
                
                table = self.query_one("#results-table", DataTable)
                table.clear(columns=True)
                table.display = True
                self.query_one("#query-results-placeholder").display = False
                
                if rows:
                    table.add_columns("CID", "Name", "Type", "NotNull", "Default", "PK")
                    for row in rows:
                        table.add_row(row["cid"], row["name"], row["type"], row["notnull"], row["dflt_value"], row["pk"])
                
                self.app.notify(f"Showing schema for table: {table_name}", severity="information")
        except Exception as e:
            self.app.notify(f"Error fetching schema: {e}", severity="error")

    async def select_database(self, db_id: str, db_name: str) -> None:
        """Fetch tables for the selected database and cache row counts."""
        self.selected_db_id = db_id
        self.query_one("#d1-main-content Label").update(f"SQL Sandbox: {db_name}")
        
        table_list = self.query_one("#table-list", ListView)
        table_list.clear()
        
        try:
            tables = await self.app.client.list_d1_tables(db_id)
            for table in tables:
                table_list.append(ListItem(Label(table)))
                
                # Skip system or internal Cloudflare tables to avoid 400 errors
                if table.startswith("_cf_") or table.startswith("sqlite_"):
                    self.table_row_counts[table] = 0
                    continue

                # Background fetch row counts for estimation (Gracefully handle individual failures)
                try:
                    count = await self.app.client.get_table_row_count(db_id, table)
                    self.table_row_counts[table] = count
                except Exception:
                    self.table_row_counts[table] = 1000 # Fallback
                
        except Exception as e:
            self.app.notify(f"Error fetching tables list: {e}", severity="error")

    async def on_input_changed(self, event: Input.Changed) -> None:
        """Debounced SQL analysis for cost estimation."""
        if event.input.id != "sql-input" or not self.selected_db_id:
            return

        if self.analysis_timer:
            self.analysis_timer.cancel()
        
        import asyncio
        async def delayed_analysis():
            await asyncio.sleep(0.5)
            await self.analyze_query(event.value)
        
        self.analysis_timer = asyncio.create_task(delayed_analysis())

    async def analyze_query(self, sql: str) -> None:
        """Analyze SQL using EXPLAIN and update the estimator widget."""
        if not sql or len(sql) < 5:
            self.query_one("#cost-estimator").update("Ready to analyze...")
            return

        # Skip non-select queries for simple analysis
        if not sql.strip().upper().startswith("SELECT"):
            self.query_one("#cost-estimator").update("Cost Estimation only supported for SELECT queries")
            return

        try:
            res = await self.app.client.query_d1(self.selected_db_id, f"EXPLAIN QUERY PLAN {sql}")
            if res.get("success"):
                plan = res["result"][0].get("results", [])
                
                # Analyze plan
                is_scan = any("SCAN" in str(p).upper() for p in plan)
                
                # Double check for SELECT * without WHERE or LIMIT (Guaranteed expensive on large tables)
                is_unfiltered_select = "SELECT" in sql.upper() and "WHERE" not in sql.upper() and "LIMIT" not in sql.upper()
                
                target_table = None
                # Crude table name extraction
                import re
                table_match = re.search(r"FROM\s+([\"\w]+)", sql, re.IGNORECASE)
                if table_match:
                    target_table = table_match.group(1).replace('"', '')

                row_count = self.table_row_counts.get(target_table, 1000)
                
                estimator = self.query_one("#cost-estimator")
                if is_scan or is_unfiltered_select:
                    if row_count > 1000:
                        estimator.update(f"[b red]🔴 DANGEROUS: Full Scan on {target_table} (~{row_count} Row Reads)[/]")
                    else:
                        estimator.update(f"[b yellow]🟡 WARNING: Table Scan on {target_table} (~{row_count} Row Reads)[/]")
                else:
                    estimator.update(f"[b green]🟢 SAFE: Query uses indexes. Estimated Row Reads: < 50[/]")
            else:
                self.query_one("#cost-estimator").update("[i red]Invalid SQL Syntax[/]")
        except Exception:
            pass

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks for Query and Explain."""
        if not self.selected_db_id:
            self.app.notify("Please select a database first.", severity="warning")
            return

        sql = self.query_one("#sql-input", Input).value
        if not sql:
            return

        if event.button.id == "run-query-btn":
            await self.run_sql(sql)
        elif event.button.id == "explain-btn":
            await self.run_sql(f"EXPLAIN QUERY PLAN {sql}")
        elif event.button.id == "refresh-db-btn":
            await self.refresh_databases()
            self.app.notify("Database list refreshed", severity="information")

    async def run_sql(self, sql: str) -> None:
        """Execute SQL and display results."""
        results_placeholder = self.query_one("#query-results-placeholder")
        results_placeholder.display = False
        
        try:
            res = await self.app.client.query_d1(self.selected_db_id, sql)
            if not res.get("success"):
                self.app.notify(f"Query Error: {res.get('errors')}", severity="error")
                return

            # D1 query returns a list of results (one per statement)
            query_res = res["result"][0]
            rows = query_res.get("results", [])
            meta = query_res.get("meta", {})
            
            # Update results table
            table = self.query_one("#results-table", DataTable)
            table.clear(columns=True)
            table.display = True
            
            if rows:
                columns = rows[0].keys()
                table.add_columns(*columns)
                for row in rows:
                    table.add_row(*[row[col] for col in columns])
            
            # Show row reads in notification for now
            row_reads = meta.get("rows_read", 0)
            
            # Smart Analysis: Check for unindexed scans in EXPLAIN
            if "EXPLAIN" in sql.upper():
                unindexed = any("SCAN TABLE" in str(r).upper() for r in rows)
                if unindexed:
                    self.app.notify("⚠️ UNINDEXED SCAN DETECTED! Consider adding an index to reduce Row Reads.", severity="error", timeout=10)
                else:
                    self.app.notify("✅ Query uses indexes efficiently.", severity="information")

            self.app.record_query(sql, row_reads, len(rows), True)
            self.app.notify(f"Success! Rows Read: {row_reads}", severity="information")
            
        except Exception as e:
            self.app.record_query(sql, 0, 0, False)
            self.app.notify(f"Execution Error: {e}", severity="error")

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="d1-sidebar", classes="sidebar"):
                yield Label("Databases")
                yield ListView(id="database-list")
                yield Button("Refresh List", id="refresh-db-btn", variant="default")
                yield Label("Tables")
                yield ListView(id="table-list")
            
            with Vertical(id="d1-main-content"):
                yield Label("SQL Sandbox", classes="section-title")
                yield Input(placeholder="SELECT * FROM table LIMIT 10", id="sql-input")
                
                # New Cost Estimator Widget
                yield Static("Ready to analyze...", id="cost-estimator")
                
                with Horizontal(id="query-actions"):
                    yield Button("Run Query", variant="primary", id="run-query-btn")
                    yield Button("Explain Plan", variant="default", id="explain-btn")
                
                yield Static("Results", id="results-label")
                yield DataTable(id="results-table")
                yield Static("No data loaded.", id="query-results-placeholder")
