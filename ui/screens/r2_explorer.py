from textual.app import ComposeResult
from textual.widgets import Static, ListView, ListItem, Label, DirectoryTree
from textual.containers import Horizontal, Vertical

class R2ExplorerScreen(Static):
    """Dual-pane explorer for R2 storage."""

    async def on_mount(self) -> None:
        """Fetch R2 buckets when the screen is mounted."""
        self.current_cursor = None
        await self.refresh_buckets()

    async def refresh_buckets(self) -> None:
        """Fetch and display R2 buckets."""
        if not hasattr(self.app, 'client') or not self.app.client:
            return

        bucket_list = self.query_one("#r2-object-list", ListView) # Reusing this for bucket selection initially
        bucket_list.clear()
        
        try:
            buckets = await self.app.client.list_r2_buckets()
            for bucket in buckets:
                bucket_list.append(ListItem(Label(f"📁 {bucket['name']}"), id=f"bucket-{bucket['name']}"))
            self.query_one("#r2-bucket-title").update("R2 Buckets")
        except Exception as e:
            self.app.notify(f"Error fetching R2: {e}", severity="error")

    async def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle bucket selection."""
        if event.item and event.item.id:
            if event.item.id.startswith("bucket-"):
                bucket_name = event.item.id.replace("bucket-", "")
                self.current_cursor = None # Reset cursor for new bucket
                await self.list_objects(bucket_name)
            elif event.item.id == "load-more-r2":
                await self.list_objects(self.selected_bucket, cursor=self.current_cursor)
            elif event.item.id == "back-to-buckets":
                await self.refresh_buckets()

    async def list_objects(self, bucket_name: str, cursor: str = None) -> None:
        """List objects in the selected bucket."""
        self.selected_bucket = bucket_name
        self.query_one("#r2-bucket-title").update(f"R2 Bucket: {bucket_name}")
        
        obj_list = self.query_one("#r2-object-list", ListView)
        if not cursor:
            obj_list.clear()
            obj_list.append(ListItem(Label(" [b]🔙 Back to Buckets[/b] "), id="back-to-buckets"))
        
        # Remove previous Load More button if it exists
        try:
            load_more = obj_list.query_one("#load-more-r2")
            load_more.remove()
        except:
            pass
        
        try:
            res_data = await self.app.client.list_r2_objects(bucket_name, cursor=cursor or "")
            objects = res_data.get("result", [])
            info = res_data.get("result_info", {})
            self.current_cursor = info.get("cursor")
            
            for obj in objects:
                size_kb = round(obj['size'] / 1024, 2)
                obj_list.append(ListItem(Label(f"📄 {obj['key']} ({size_kb} KB)")))
            
            if info.get("is_truncated"):
                obj_list.append(ListItem(Label(" [b]⬇️ Load More...[/b] "), id="load-more-r2"))
            
            if not objects and not cursor:
                obj_list.append(ListItem(Label("Bucket is empty.")))
                
        except Exception as e:
            self.app.notify(f"Error listing objects: {e}", severity="error")

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(classes="explorer-pane"):
                yield Label("Local Filesystem")
                yield DirectoryTree("./", id="local-tree")
            
            with Vertical(classes="explorer-pane"):
                yield Label("R2 Bucket: [Select Bucket]", id="r2-bucket-title")
                yield ListView(id="r2-object-list")
                yield Static("Bucket metadata summary...", id="r2-bucket-meta")
        
        yield Static("Press 'Enter' to preview, 'C' to copy between panes.", id="explorer-help")
