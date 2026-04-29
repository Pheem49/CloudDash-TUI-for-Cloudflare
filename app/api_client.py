import os
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from app.logger import log_error, log_warning, log_debug, log_info

load_dotenv()

class CloudflareClient:
    def __init__(self, api_token: Optional[str] = None, account_id: Optional[str] = None):
        self.api_token = api_token or os.getenv("CLOUDFLARE_API_TOKEN")
        self.account_id = account_id or os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.timeout = httpx.Timeout(30.0)
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
        
        if not self.api_token:
            raise ValueError("Cloudflare API Token is missing.")
        if not self.account_id:
            raise ValueError("Cloudflare Account ID is missing.")

        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        
        log_info("Cloudflare API Client initialized")

    async def _get(self, endpoint: str) -> Dict[str, Any]:
        """GET request with retry logic."""
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    url = f"{self.base_url}/accounts/{self.account_id}/{endpoint}"
                    response = await client.get(url, headers=self.headers)
                    response.raise_for_status()
                    log_debug(f"GET {endpoint} - Success")
                    return response.json()
            except httpx.TimeoutException:
                log_warning(f"Timeout on GET {endpoint} (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise
            except httpx.HTTPStatusError as e:
                log_error(f"HTTP Error on GET {endpoint}: {e.status_code}")
                if e.status_code == 429:  # Rate limit
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    else:
                        raise
                else:
                    raise
            except Exception as e:
                log_error(f"Error on GET {endpoint}: {str(e)}", exc_info=True)
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    raise

    async def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """POST request with retry logic."""
        for attempt in range(self.max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    url = f"{self.base_url}/accounts/{self.account_id}/{endpoint}"
                    response = await client.post(url, headers=self.headers, json=data)
                    response.raise_for_status()
                    log_debug(f"POST {endpoint} - Success")
                    return response.json()
            except httpx.TimeoutException:
                log_warning(f"Timeout on POST {endpoint} (attempt {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise
            except httpx.HTTPStatusError as e:
                log_error(f"HTTP Error on POST {endpoint}: {e.status_code}")
                if e.status_code == 429:  # Rate limit
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    else:
                        raise
                else:
                    raise
            except Exception as e:
                log_error(f"Error on POST {endpoint}: {str(e)}", exc_info=True)
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                else:
                    raise

    # --- D1 API ---
    async def list_d1_databases(self) -> List[Dict[str, Any]]:
        try:
            data = await self._get("d1/database")
            log_info(f"Retrieved {len(data.get('result', []))} D1 databases")
            return data.get("result", [])
        except Exception as e:
            log_error(f"Failed to list D1 databases: {e}")
            raise

    async def query_d1(self, database_id: str, sql: str, params: List[Any] = None) -> Dict[str, Any]:
        try:
            endpoint = f"d1/database/{database_id}/query"
            payload = {"sql": sql, "params": params or []}
            result = await self._post(endpoint, payload)
            log_debug(f"D1 Query executed: {sql[:50]}...")
            return result
        except Exception as e:
            log_error(f"Failed to execute D1 query: {e}")
            raise

    async def explain_d1(self, database_id: str, sql: str) -> Dict[str, Any]:
        try:
            return await self.query_d1(database_id, f"EXPLAIN QUERY PLAN {sql}")
        except Exception as e:
            log_error(f"Failed to explain D1 query: {e}")
            raise

    async def list_d1_tables(self, database_id: str) -> List[str]:
        """List all tables in a D1 database."""
        try:
            res = await self.query_d1(database_id, "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            if res.get("success"):
                tables = [row["name"] for row in res["result"][0]["results"]]
                log_info(f"Retrieved {len(tables)} tables from D1 database")
                return tables
            return []
        except Exception as e:
            log_error(f"Failed to list D1 tables: {e}")
            raise

    async def get_table_row_count(self, database_id: str, table_name: str) -> int:
        """Get approximate row count for a table."""
        try:
            res = await self.query_d1(database_id, f'SELECT COUNT(*) as count FROM "{table_name}"')
            if res.get("success"):
                count = res["result"][0]["results"][0]["count"]
                log_debug(f"Table {table_name} has {count} rows")
                return count
            return 0
        except Exception as e:
            log_warning(f"Failed to get row count for {table_name}: {e}")
            return 0

    # --- R2 API ---
    async def list_r2_buckets(self) -> List[Dict[str, Any]]:
        try:
            data = await self._get("r2/buckets")
            buckets = data.get("result", {}).get("buckets", [])
            log_info(f"Retrieved {len(buckets)} R2 buckets")
            return buckets
        except Exception as e:
            log_error(f"Failed to list R2 buckets: {e}")
            raise

    async def list_r2_objects(self, bucket_name: str, prefix: str = "", delimiter: str = "", limit: int = 100, cursor: str = "") -> Dict[str, Any]:
        try:
            url = f"r2/buckets/{bucket_name}/objects?prefix={prefix}&delimiter={delimiter}&limit={limit}"
            if cursor:
                url += f"&cursor={cursor}"
            data = await self._get(url)
            log_debug(f"Retrieved R2 objects from {bucket_name}")
            return data
        except Exception as e:
            log_error(f"Failed to list R2 objects in {bucket_name}: {e}")
            raise
    
    # --- Account API ---
    async def verify_credentials(self) -> bool:
        """Verify that API token and account ID are valid."""
        try:
            # Try to fetch account details
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/accounts/{self.account_id}"
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                log_info("API credentials verified successfully")
                return True
        except Exception as e:
            log_error(f"Failed to verify credentials: {e}")
            return False
