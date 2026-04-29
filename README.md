# ☁️ CloudDash: TUI for Cloudflare

A premium, high-performance **Terminal User Interface (TUI)** for managing Cloudflare D1 and R2 resources. Designed for developers who prefer the speed of the terminal over the web dashboard.

<p align="center">
  <img src="assets/CloudDash.png" alt="CloudDash Logo" width="600">
</p>

> [!IMPORTANT]
> **Disclaimer:** This is a community-led open-source project and is **not affiliated with, authorized, maintained, or endorsed by Cloudflare, Inc.** "Cloudflare" is a registered trademark of Cloudflare, Inc.

Inspired by tools like `k9s` and `lazygit`, **CloudDash** focuses on **Performance Optimization** and **Cost Transparency** (Row Reads monitoring).

---

## ✨ Features

### 📊 Live Row-Read Monitor (Dashboard)

- **Real-time Tracking:** See exactly how many Row Reads each query consumes.
- **Cost Awareness:** Visual indicators (Green/Yellow/Red) warn you about expensive queries.
- **Query History:** Keep track of your recent activities across all databases (persistent across sessions).
- **Daily Statistics:** View total queries, success/error rates, and average query efficiency.

### 🗄️ D1 Database Management

- **Schema Explorer:** Instantly view table structures, columns, and indexes (supports special characters and system tables).
- **SQL Sandbox:** Write and execute SQL queries with a smooth, responsive data grid.
- **Smart Explain:** Built-in integration with `EXPLAIN QUERY PLAN` that automatically detects and warns you about **Unindexed Scans**.
- **Quick Refresh:** Dedicated refresh button to sync your database list instantly.
- **Cost Estimator:** Real-time query analysis with visual warnings for potentially expensive queries.

### 📦 R2 Storage Explorer

- **Dual-Pane Interface:** Browse your local filesystem and R2 buckets side-by-side.
- **Smart Pagination:** Support for buckets with thousands of files using the **"Load More"** system.
- **Easy Navigation:** Quickly switch between buckets with the **"Back to Buckets"** shortcut.
- **Object Details:** View file sizes and keys in a clean, scrollable list.

### ⚙️ Live Configuration (Settings)

- **Status Check:** Real-time verification of your API Token and Account ID.
- **Masked Security:** Displays loaded credentials securely (masked) to confirm `.env` is working correctly.
- **Daily Stats:** View today's query statistics including success rate and efficiency metrics.
- **Connection Verification:** Automatic validation of Cloudflare API connection.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- A Cloudflare API Token (Permissions: `D1:Edit`, `R2:Edit`, `Account Settings:Read`)
- Your Cloudflare Account ID

### ⚡ Easiest Way (Interactive Setup)

The quickest way to get started is using our setup script:

```bash
git clone https://github.com/Pheem49/CloudDash-TUI-for-Cloudflare.git
cd CloudDash-TUI-for-Cloudflare
bash setup.sh
```
The script will automatically create a virtual environment, install dependencies, and help you configure your API keys.
#### Linux / macOS
```bash
# Run the setup script
bash setup.sh

# Start the app
./clouddash
```

> [!TIP]
> **Run from anywhere:** To run CloudDash from any directory, add an alias to your `.bashrc` or `.zshrc`:
> ```bash
> echo "alias clouddash='$(pwd)/clouddash'" >> ~/.bashrc && source ~/.bashrc
> ```
> Now you can just type `clouddash` in any terminal window!

#### Windows
```powershell
.\setup.ps1
.\clouddash.bat
```

### Manual Installation

If you prefer to do it yourself:

1. **Set up Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration:**
   Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Run:**
   ```bash
   python main.py
   ```

---

## 🎮 Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `d` | Toggle Dark Mode |
| `q` | Quit Application |
| `Tab` | Switch between tabs |
| `Enter` | Select/Open item |
| `Ctrl+C` | Force quit |

---

## 📋 Troubleshooting

### "Configuration Error: API keys missing in .env"

**Solution:** Create or update your `.env` file with your Cloudflare credentials:
```bash
CLOUDFLARE_API_TOKEN=your_api_token_here
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
```

Then restart CloudDash.

**How to find your credentials:**
1. Go to https://dash.cloudflare.com/
2. API Token: Go to "My Profile" → "API Tokens" → Create a token with D1 and R2 permissions
3. Account ID: Found in the URL after logging in (look for account/[YOUR_ACCOUNT_ID])

### "Query Error: Invalid SQL Syntax"

**Solution:** Check your SQL syntax. CloudDash uses SQLite for D1, so make sure:
- Table/column names with special characters are wrapped in double quotes: `"_cf_KV"`
- SQL statements are properly terminated with semicolons
- Try the query in the Cloudflare dashboard first to verify syntax

### "UNINDEXED SCAN DETECTED"

**This is expected behavior!** CloudDash warns you about potentially expensive queries. To fix:
1. Add indexes to your heavily queried columns
2. Use WHERE clauses or LIMIT to reduce scanned rows
3. Review your EXPLAIN QUERY PLAN output for optimization hints

### Slow Performance on Large Buckets

**Solution:** CloudDash uses smart pagination for R2:
- Use the "Load More" button to paginate through large buckets
- The app loads 100 objects at a time by default
- This prevents overwhelming the terminal

### Application Won't Start

**Check logs:** CloudDash creates logs in the `logs/` directory:
```bash
cat logs/clouddash_$(date +%Y%m%d).log
```

**Common issues:**
- Python version < 3.10: Update to Python 3.10 or higher
- Missing dependencies: Run `pip install -r requirements.txt`
- Terminal compatibility: Use a terminal that supports 256 colors (most modern terminals do)

---

## 📊 Query History

CloudDash automatically saves your query history to `.clouddash_query_history.json`. This includes:
- Query SQL
- Row reads and rows returned
- Success/error status
- Timestamp
- Database name

To clear history:
1. Go to Settings tab (check if supported in your version)
2. Or manually delete: `rm .clouddash_query_history.json`

---

## 🛠️ Tech Stack

- **Framework:** [Textual](https://textual.textualize.io/) (Python TUI Framework)
- **API Client:** [HTTPX](https://www.python-httpx.org/) (Async HTTP)
- **Environment:** [Python-dotenv](https://github.com/theskumar/python-dotenv)
- **Styling:** Custom TCSS (Textual CSS)
- **Logging:** Python built-in logging module

---

## 🔒 Security

- CloudDash **never** sends your credentials anywhere except to Cloudflare's official API
- Credentials are only read from your local `.env` file
- API tokens are masked in the Settings tab for security
- All code is open-source and auditable

---

## 📝 License

MIT License.

---

## 🤝 Contributing

Found a bug? Want to contribute? Check out the issues or submit a pull request!

---

_Created with ❤️ by [Apisit Promma](https://github.com/pheem49) for CloudDash Developers._
