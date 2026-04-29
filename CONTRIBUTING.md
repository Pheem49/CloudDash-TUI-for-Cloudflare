# Contributing to CloudDash

Thank you for your interest in contributing to CloudDash! This document provides guidelines and instructions for contributing to the project.

## 🎯 Code of Conduct

Be respectful, inclusive, and constructive in all interactions. We welcome contributions from developers of all skill levels.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Git
- A Cloudflare API Token (for testing)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/Pheem49/CloudDash-TUI-for-Cloudflare.git
cd CloudDash-TUI-for-Cloudflare

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies in development mode
pip install -r requirements.txt

# Create .env file for testing
cp .env.example .env
# Edit .env with your test credentials
```

---

## 📋 How to Contribute

### 1. **Report Bugs**

Create an issue with:
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Relevant logs from `logs/` directory

### 2. **Suggest Features**

Describe:
- The feature and its use case
- Why it would be valuable
- Potential implementation approach

### 3. **Submit Pull Requests**

1. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes:**
   - Follow the coding style below
   - Add comments for complex logic
   - Update docstrings

3. **Test your changes:**
   ```bash
   # Check syntax
   python3 -m py_compile app/*.py ui/**/*.py
   
   # Run component tests
   python3 -c "from main import main; from ui.app import CloudDashApp; print('✅ Imports OK')"
   ```

4. **Commit with clear messages:**
   ```bash
   git commit -m "feat: add feature description"
   # Use: feat, fix, docs, style, refactor, test, chore
   ```

5. **Push and create PR:**
   ```bash
   git push origin feature/your-feature-name
   ```

---

## 🎨 Coding Style

### Python Code
- Use **type hints** for all functions (required)
- Follow **PEP 8** style guide
- Use descriptive variable names
- Max line length: 100 characters
- Use docstrings for all public functions

### Example:
```python
from typing import List, Dict, Any

def process_data(items: List[Dict[str, Any]], limit: int = 10) -> List[str]:
    """
    Process a list of items and return results.
    
    Args:
        items: List of dictionaries to process
        limit: Maximum number of items to process
        
    Returns:
        List of processed strings
    """
    results: List[str] = []
    for item in items[:limit]:
        results.append(str(item))
    return results
```

### Logging
Use the logging system instead of print:
```python
from app.logger import log_info, log_error, log_debug

log_info("Operation completed successfully")
log_error(f"Failed to fetch data: {error}")
log_debug("Detailed debug information")
```

---

## 📁 Project Structure

```
CloudDash/
├── app/
│   ├── api_client.py       # Cloudflare API wrapper
│   ├── logger.py           # Logging system
│   ├── query_history.py    # Query persistence
│   └── __init__.py
├── ui/
│   ├── app.py             # Main Textual app
│   ├── style.tcss         # Styling
│   ├── screens/
│   │   ├── dashboard.py   # Row-read monitor
│   │   ├── d1_manager.py  # Database management
│   │   ├── r2_explorer.py # Storage explorer
│   │   └── __init__.py
│   ├── widgets/           # Custom widgets
│   └── __init__.py
├── main.py               # Entry point
├── requirements.txt      # Dependencies
├── pyproject.toml       # Package metadata
├── README.md            # Documentation
├── CHANGELOG.md         # Version history
└── CONTRIBUTING.md      # This file
```

---

## 🔧 Development Tips

### Running Tests
```bash
# Test imports
python3 -c "import app.logger; import app.api_client; print('OK')"

# Test with sample data
python3 << EOF
from app.query_history import get_query_history
qh = get_query_history()
qh.add_query("SELECT 1", 5, 1, True, "test", "test_table")
print(f"History: {len(qh.get_history())} entries")
EOF
```

### Debugging
1. Check logs: `cat logs/clouddash_*.log`
2. Use log_debug() in code for detailed tracing
3. Test isolated components before integration

### Version Pinning
When updating dependencies, use version ranges:
```
package>=1.0.0,<2.0.0  # Good - prevents breaking changes
package==1.0.0         # Avoid - too strict
package>=1.0.0         # Avoid - could break unexpectedly
```

---

## 📝 Documentation

When adding features:
1. Update README.md if it's a user-facing feature
2. Update CHANGELOG.md in the "Planned" section
3. Add docstrings to all functions
4. Add type hints to all function signatures

---

## 🐛 Known Issues

Check the [Issues page](https://github.com/Pheem49/CloudDash-TUI-for-Cloudflare/issues) before starting work.

---

## 📞 Questions?

- Check existing issues and discussions
- Review the README troubleshooting section
- Create a new discussion if needed

---

## ✅ Before Submitting PR

- [ ] Code follows PEP 8 style
- [ ] Type hints added to all functions
- [ ] Docstrings updated
- [ ] No breaking changes (or clearly documented)
- [ ] Tested with sample data
- [ ] Commit messages are clear
- [ ] Logs checked for errors
- [ ] README/CHANGELOG updated if needed

---

Thank you for contributing to CloudDash! Your help makes this tool better for everyone. 🙏
