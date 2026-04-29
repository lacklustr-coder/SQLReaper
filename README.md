# SQLReaper

<div align="center">

## &#9760; SQLReaper v2.1 Advanced

**Enterprise-Grade SQL Injection Penetration Testing Framework**

_[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org) [![Flask](https://img.shields.io/badge/Flask-3.x-green.svg)](https://flask.palletsprojects.com/) [![License](https://img.shields.io/badge/License-GPLv3-lightgrey.svg)](LICENSE) [![AI Powered](https://img.shields.io/badge/AI-Powered-purple.svg)](FEATURES.md)_

A powerful, enterprise-grade penetration testing framework featuring **AI-powered vulnerability analysis**, **advanced WAF bypass techniques**, **real-time WebSocket monitoring**, and **JWT authentication**. Includes 300+ pre-built Google dorks, automated exploitation chain discovery, and comprehensive reporting.

### 🔥 **NEW in v2.1 Advanced:**
- 🧠 **AI-Powered Analysis** - Automatic vulnerability classification and remediation suggestions
- 🛡️ **WAF Bypass Engine** - ML-based payload mutation with 9+ evasion techniques  
- 🔐 **Multi-User Auth** - JWT-based authentication with RBAC
- 📡 **Real-Time Monitoring** - WebSocket-based live scan streaming
- ⚡ **Exploitation Chains** - Automated vulnerability chaining analysis
- 🎯 **Advanced Fuzzing** - 8+ injection type support with custom payloads

**[📖 View Full Feature List](FEATURES.md)**

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
- [sqlmap](https://github.com/sqlmapproject/sqlmap) installed (optional, can configure later)
- Windows, Linux, or macOS

### Security Note
SQLReaper includes [Aikido](https://www.aikido.dev/) security scanning for dependency vulnerability monitoring. See [AIKIDO_SETUP.md](AIKIDO_SETUP.md) for setup instructions.

### Quick Start (Windows)

**First Time Setup:**
```batch
# Run the setup wizard (installs dependencies, creates directories)
setup.bat
```

**Start SQLReaper:**
```batch
# Launch the application
start.bat
```

**Try the Demo:**
```batch
# Run interactive API demo (in a separate window)
demo.bat
```

### Manual Installation (All Platforms)

```bash
# 1. Clone or download SQLReaper
git clone <your-repo-url>
cd SQLReaper

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Install sqlmap
git clone https://github.com/sqlmapproject/sqlmap.git

# 4. Start the application
python sqlmap_gui/app.py

# 5. Open your browser
# Visit: http://localhost:5000
```

### Default Login

```
Username: admin
Password: admin123
```

⚠️ **IMPORTANT:** Change the default password immediately in production!

### Configuration

1. **Web Interface**: Open http://localhost:5000
2. **Login**: Use default credentials (admin/admin123)
3. **Settings**: Click Settings (&#9881;) to configure:
   - **SQLMap Path** - Full path to sqlmap.py
   - **Proxy** - HTTP proxy settings  
   - **Auth Header** - Authentication headers
4. **API Access**: Get JWT token from `/api/auth/login`

### Environment Variables (Optional)

```batch
# Windows
set SQLMAP_PATH=C:\path\to\sqlmap.py
set JWT_SECRET=your-secret-key-here

# Linux/Mac
export SQLMAP_PATH=/path/to/sqlmap.py
export JWT_SECRET=your-secret-key-here
```

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