"""Query history persistence for CloudDash."""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.logger import log_debug, log_error, log_info

HISTORY_FILE: str = ".clouddash_query_history.json"
MAX_HISTORY_ENTRIES: int = 500

class QueryHistory:
    """Manages query history persistence."""
    
    def __init__(self) -> None:
        self.history: List[Dict[str, Any]] = self._load_history()
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load query history from file."""
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, 'r') as f:
                    history: List[Dict[str, Any]] = json.load(f)
                    log_debug(f"Loaded {len(history)} query history entries")
                    return history
        except Exception as e:
            log_error(f"Failed to load query history: {e}")
        return []
    
    def _save_history(self) -> None:
        """Save query history to file."""
        try:
            # Keep only the most recent entries
            history_to_save: List[Dict[str, Any]] = self.history[:MAX_HISTORY_ENTRIES]
            
            with open(HISTORY_FILE, 'w') as f:
                json.dump(history_to_save, f, indent=2)
            log_debug(f"Saved {len(history_to_save)} query history entries")
        except Exception as e:
            log_error(f"Failed to save query history: {e}")
    
    def add_query(self, sql: str, rows_read: int, rows_returned: int, 
                  success: bool, database: str = "", table: str = "") -> None:
        """Add a query to history."""
        entry: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "time": datetime.now().strftime("%H:%M:%S"),
            "sql": sql,
            "rows_read": rows_read,
            "rows_returned": rows_returned,
            "status": "Success" if success else "Error",
            "database": database,
            "table": table
        }
        self.history.insert(0, entry)
        
        # Trim to max entries
        if len(self.history) > MAX_HISTORY_ENTRIES:
            self.history = self.history[:MAX_HISTORY_ENTRIES]
        
        self._save_history()
        log_debug(f"Added query to history: {sql[:50]}...")
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get all query history."""
        return self.history
    
    def get_today_stats(self) -> Dict[str, Any]:
        """Get statistics for today's queries."""
        today = datetime.now().date()
        today_queries: List[Dict[str, Any]] = [
            q for q in self.history 
            if datetime.fromisoformat(q["timestamp"]).date() == today
        ]
        
        total_reads: int = sum(q["rows_read"] for q in today_queries if q["status"] == "Success")
        successful_count: int = sum(1 for q in today_queries if q["status"] == "Success")
        failed_count: int = sum(1 for q in today_queries if q["status"] == "Error")
        total_returned: int = sum(q.get("rows_returned", 0) for q in today_queries if q["status"] == "Success")
        
        return {
            "total_queries": successful_count + failed_count,
            "successful": successful_count,
            "failed": failed_count,
            "total_row_reads": total_reads,
            "total_rows_returned": total_returned,
            "avg_efficiency": (total_returned / total_reads * 100) if total_reads > 0 else 0
        }
    
    def clear_history(self) -> None:
        """Clear all query history."""
        self.history = []
        try:
            if os.path.exists(HISTORY_FILE):
                os.remove(HISTORY_FILE)
            log_info("Query history cleared")
        except Exception as e:
            log_error(f"Failed to clear query history: {e}")

# Global instance
_query_history: Optional[QueryHistory] = None

def get_query_history() -> QueryHistory:
    """Get the global query history instance."""
    global _query_history
    if _query_history is None:
        _query_history = QueryHistory()
    return _query_history
