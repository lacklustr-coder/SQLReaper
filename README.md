# SQLReaper

<div align="center">

## &#9760; SQLReaper v2.1

**Advanced SQL Injection Penetration Testing Framework - GUI**

_[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org) [![Flask](https://img.shields.io/badge/Flask-3.x-green.svg)](https://flask.palletsprojects.com/) [![License](https://img.shields.io/badge/License-GPLv3-lightgrey.svg)](LICENSE)_

A powerful, modern GUI wrapper for [sqlmap](https://github.com/sqlmapproject/sqlmap) with 300+ pre-built Google dorks, batch scanning, profiles, and more.

</div>

---

## Features

### &#128269; Google Dorking
- 300+ pre-built dork queries organized by category
- Two-column library layout with difficulty badges
- Quick preset buttons for common targets
- Filter by difficulty (Easy/Medium/Hard/Advanced)
- Search across all dorks instantly

### &#127919; Direct Scan
- Full sqlmap parameter support via GUI
- Enumeration options (databases, tables, columns, dump)
- Advanced options (risk, level, tamper, OS shell)
- Custom options textarea

### &#128202; Batch Scanning
- Scan up to 50 URLs simultaneously
- Per-URL results with vulnerability status
- Configurable scan options

### &#128203; Multi-Dork Scanner
- Run multiple dork queries at once
- Generate sqlmap commands for each dork
- Copy-to-clipboard for individual scanning

### &#128190; Scan Profiles
- Save custom scan configurations
- Load profiles for quick scanning
- Delete unused profiles

### &#128196; Export & History
- Export results as TXT, MD, HTML, or JSON
- Full scan history with timestamp tracking
- Bookmark and re-run previous scans

### &#9881; Settings
- Configurable SQLMap path (supports any location)
- Proxy configuration
- Authentication headers

### &#128274; Security
- Integrated [Aikido](https://www.aikido.dev/) security scanning
- Automated vulnerability detection
- Dependency tracking with lockfile
- OWASP Top 10 compliance monitoring

## Screenshot

<p align="center">
  <em>Dark & Light theme support. Modern hacker-friendly interface.</em>
</p>

## Installation

### Prerequisites
- Python 3.8 or higher
- [sqlmap](https://github.com/sqlmapproject/sqlmap) installed
- Windows, Linux, or macOS

### Security Note
SQLReaper includes [Aikido](https://www.aikido.dev/) security scanning for dependency vulnerability monitoring. See [AIKIDO_SETUP.md](AIKIDO_SETUP.md) for setup instructions.

### Quick Start

**Windows:**
```batch
double-click start.bat
```

**Manual:**
```bash
# Clone or set your sqlmap path
git clone https://github.com/sqlmapproject/sqlmap.git

# Install dependencies (using lockfile for security)
pip install -r requirements-lock.txt

# Or install from requirements.txt
pip install -r requirements.txt

# Start the GUI
cd "sqlmap project\sqlmap_gui"
python app.py
```

### Configuration

1. Open http://localhost:5000 in your browser
2. Click Settings (&#9881;) to configure:
   - **SQLMap Path** - Full path to sqlmap.py
   - **Proxy** - HTTP proxy settings
   - **Auth Header** - Authentication headers

## Project Structure

```
SQLReaper/
├── sqlmap_gui/
│   ├── app.py              # Flask backend & API routes
│   ├── enhancements.py     # Auto-save, tray module
│   ├── templates/
│   │   └── index.html      # Main GUI interface
│   └── static/
│       ├── css/
│       │   └── style.css   # Dark/Light theme styles
│       └── js/
│           └── main.js     # Frontend logic
├── results/                # Scan results storage
├── profiles/               # Saved scan profiles
├── uploads/                # File uploads
├── start.bat              # Windows startup script
└── README.md              # This file
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/scan` | POST | Direct URL scan |
| `/api/google-dork` | POST | Google dork scan |
| `/api/google-dork-multi` | POST | Multi-dork scan |
| `/api/scan/batch` | POST | Batch URL scan |
| `/api/settings` | GET/POST | Get/Save settings |
| `/api/history` | GET | Load scan history |
| `/api/profiles` | GET/POST | Manage profiles |
| `/api/export` | POST | Export results |

## Dork Categories

- Basic & Advanced SQLi URL Dorks
- ASP/ASPX/JSP Dorks
- Search & Query Parameter Dorks
- Product & Shop Dorks
- News & Article Dorks
- Document & File Dorks
- Login & Admin Panel Dorks
- Form & Input Parameter Dorks
- International Domain Dorks
- CMS & WordPress Dorks
- Directory Listing & Index Dorks
- Authentication & Session Dorks
- Error-Based SQLi Dorks
- Sensitive Data Exposure Dorks
- Injection-Ready Complex Dorks

## Disclaimer

**This tool is for authorized security testing only.** Always obtain proper authorization before testing any target. The authors are not responsible for misuse of this tool.

## Credits

- [sqlmap](https://github.com/sqlmapproject/sqlmap) - The underlying SQL injection tool
- Flask - Backend web framework
- CustomTkinter-inspired design patterns

## License

[GPL v3.0](LICENSE)

---

<div align="center">
<em>Built for penetration testers and security researchers.</em>
</div>