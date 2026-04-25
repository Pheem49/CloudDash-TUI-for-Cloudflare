import os
import httpx
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class CloudflareClient:
    def __init__(self, api_token: Optional[str] = None, account_id: Optional[str] = None):
        self.api_token = api_token or os.getenv("CLOUDFLARE_API_TOKEN")
        self.account_id = account_id or os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.base_url = "https://api.cloudflare.com/client/v4"
        
        if not self.api_token:
            raise ValueError("Cloudflare API Token is missing.")
        if not self.account_id:
            raise ValueError("Cloudflare Account ID is missing.")

        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    async def _get(self, endpoint: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/accounts/{self.account_id}/{endpoint}", headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/accounts/{self.account_id}/{endpoint}", headers=self.headers, json=data)
            response.raise_for_status()
            return response.json()

    # --- D1 API ---
    async def list_d1_databases(self) -> List[Dict[str, Any]]:
        data = await self._get("d1/database")
        return data.get("result", [])

    async def query_d1(self, database_id: str, sql: str, params: List[Any] = None) -> Dict[str, Any]:
        endpoint = f"d1/database/{database_id}/query"
        payload = {"sql": sql, "params": params or []}
        return await self._post(endpoint, payload)

    async def explain_d1(self, database_id: str, sql: str) -> Dict[str, Any]:
        return await self.query_d1(database_id, f"EXPLAIN QUERY PLAN {sql}")

    async def list_d1_tables(self, database_id: str) -> List[str]:
        # D1 doesn't have a direct 'list tables' endpoint easily found in basic docs, 
        # usually we query sqlite_master
        res = await self.query_d1(database_id, "SELECT name FROM sqlite_master WHERE type='table'")
        if res.get("success"):
            return [row["name"] for row in res["result"][0]["results"]]
        return []

    async def get_table_row_count(self, database_id: str, table_name: str) -> int:
        """Get approximate row count for a table."""
        res = await self.query_d1(database_id, f'SELECT COUNT(*) as count FROM "{table_name}"')
        if res.get("success"):
            return res["result"][0]["results"][0]["count"]
        return 0

    # --- R2 API ---
    async def list_r2_buckets(self) -> List[Dict[str, Any]]:
        data = await self._get("r2/buckets")
        return data.get("result", {}).get("buckets", [])

    async def list_r2_objects(self, bucket_name: str, prefix: str = "", delimiter: str = "", limit: int = 100, cursor: str = "") -> Dict[str, Any]:
        url = f"r2/buckets/{bucket_name}/objects?prefix={prefix}&delimiter={delimiter}&limit={limit}"
        if cursor:
            url += f"&cursor={cursor}"
        data = await self._get(url)
        # Return full data to access result_info for pagination
        return data
