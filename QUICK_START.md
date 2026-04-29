# SQLReaper v2.1 Advanced - Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Setup (First Time Only)

**Windows Users:**
```batch
setup.bat
```

**Everyone Else:**
```bash
pip install -r requirements.txt
```

### Step 2: Launch

**Windows:**
```batch
start.bat
```

**Linux/Mac:**
```bash
python sqlmap_gui/app.py
```

### Step 3: Login

1. Open browser to: **http://localhost:5000**
2. Login with:
   - Username: `admin`
   - Password: `admin123`
3. **Change password immediately!**

---

## 📁 Batch Files Overview

| File | Purpose |
|------|---------|
| **setup.bat** | First-time setup wizard (install dependencies, create directories) |
| **start.bat** | Launch SQLReaper application |
| **demo.bat** | Run interactive API demo |

---

## 🎯 Common Tasks

### Run a Basic Scan

1. Go to **Direct Scan** tab
2. Enter target URL: `http://example.com/page.php?id=1`
3. Check **Batch Mode**
4. Click **Start Scan**
5. Watch real-time output

### Use AI Analysis

**Analyze an injection:**
```bash
curl -X POST http://localhost:5000/api/ai/analyze-injection \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "response": "mysql_fetch_array() error...",
    "payload": "'\'' OR '\''1'\''='\''1"
  }'
```

### Generate WAF Bypasses

**Create bypass payloads:**
```bash
curl -X POST http://localhost:5000/api/waf/generate-bypasses \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payload": "'\'' UNION SELECT 1,2,3--",
    "count": 10
  }'
```

### Get JWT Token

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

---

## 🔍 Key Features Quick Reference

### Web Interface Tabs

| Tab | What It Does |
|-----|--------------|
| **Direct Scan** | Single URL scanning with full options |
| **Batch Scan** | Multiple URL scanning |
| **Google Dorking** | Single dork search |
| **Multi-Dork** | Multiple dork searches |
| **Dork Library** | 300+ pre-built dork queries |
| **Templates** | Pre-configured scan profiles |
| **Vulnerabilities** | Track and manage findings |
| **Fuzzer** | Parameter fuzzing engine |
| **Queue** | Scheduled and queued scans |
| **Statistics** | Scan metrics and analytics |
| **Profiles** | Save/load scan configurations |

### API Endpoints Categories

| Category | Endpoints | Purpose |
|----------|-----------|---------|
| **Auth** | `/api/auth/*` | Login, register, user management |
| **AI Analysis** | `/api/ai/*` | Vulnerability analysis, WAF detection, remediation |
| **WAF Bypass** | `/api/waf/*` | Payload mutation, bypass generation |
| **Vulnerabilities** | `/api/vulnerabilities` | Manage discovered vulnerabilities |
| **Templates** | `/api/templates` | Scan configuration templates |
| **Payloads** | `/api/payloads` | Custom payload library |
| **Fuzzing** | `/api/fuzz/*` | Parameter fuzzing |
| **Queue** | `/api/queue` | Scan queue management |
| **Reports** | `/api/reports/*` | Generate reports (HTML/MD/JSON/CSV) |
| **Statistics** | `/api/statistics` | Scan analytics |

---

## 🛠️ Configuration

### Set SQLMap Path

**Option 1 - Environment Variable (Recommended):**
```batch
# Windows
set SQLMAP_PATH=C:\path\to\sqlmap.py

# Linux/Mac
export SQLMAP_PATH=/path/to/sqlmap.py
```

**Option 2 - Web Interface:**
1. Click Settings ⚙️ icon
2. Enter SQLMap path
3. Click Save

### Set JWT Secret (Production)

```batch
# Windows
set JWT_SECRET=your-very-secure-random-string-here

# Linux/Mac
export JWT_SECRET=your-very-secure-random-string-here
```

---

## 🐛 Troubleshooting

### Application Won't Start

**Problem:** Port 5000 already in use
```bash
# Windows - Find and kill process
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :5000
kill -9 <PID>
```

**Problem:** Missing dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

**Problem:** Database errors
```bash
# Delete and recreate database
del sqlmap_gui\scans.db  # Windows
rm sqlmap_gui/scans.db   # Linux/Mac
```

### Can't Login

**Solution:** Use default credentials:
- Username: `admin`
- Password: `admin123`

If you changed the password and forgot it, reset by deleting the database.

### Import Errors

Make sure you're running from the SQLReaper root directory:
```bash
cd C:\path\to\SQLReaper
python sqlmap_gui/app.py
```

---

## 📚 Documentation

| Document | When to Read |
|----------|--------------|
| **QUICK_START.md** | This file - getting started |
| **README.md** | General overview and installation |
| **FEATURES.md** | Complete feature list with examples |
| **CHANGELOG.md** | What's new in this version |
| **PROJECT_STATUS.md** | Testing checklist and status |
| **SECURITY.md** | Security policies |
| **AIKIDO_SETUP.md** | Security scanning setup |

---

## 🎓 Learning Path

### Beginner
1. ✅ Run `setup.bat` and `start.bat`
2. ✅ Try a basic Direct Scan
3. ✅ Explore the Dork Library
4. ✅ Check the Statistics tab

### Intermediate
1. ✅ Use scan Templates
2. ✅ Try the Fuzzer
3. ✅ Explore Vulnerability tracking
4. ✅ Generate reports

### Advanced
1. ✅ Use the API with JWT authentication
2. ✅ Run `demo.bat` to see AI features
3. ✅ Generate WAF bypass payloads
4. ✅ Analyze exploitation chains
5. ✅ Set up custom scripts

---

## 🔐 Security Best Practices

### For Testing
- ✅ Only test systems you own or have permission to test
- ✅ Use in isolated lab environments
- ✅ Follow responsible disclosure practices

### For Production
- ✅ Change default password immediately
- ✅ Set custom JWT_SECRET
- ✅ Enable HTTPS
- ✅ Implement IP whitelisting
- ✅ Regular security updates
- ✅ Monitor access logs

---

## 💡 Pro Tips

1. **Save Time**: Use Templates instead of configuring scans from scratch
2. **Stay Stealthy**: Enable rate limiting and random delays in Settings
3. **Bypass WAFs**: Use the AI WAF detection first, then generate targeted bypasses
4. **Chain Attacks**: Use exploitation chain analysis to find combo vulnerabilities
5. **Automate**: Use the Queue to schedule scans during off-peak hours
6. **Learn from AI**: Review remediation suggestions to understand how to fix issues
7. **Export Everything**: Generate reports in multiple formats for different audiences

---

## 📞 Need Help?

1. Check this guide first
2. Review [FEATURES.md](FEATURES.md) for detailed examples
3. Check [PROJECT_STATUS.md](PROJECT_STATUS.md) for testing checklist
4. Review error messages in the console output

---

## ⚡ Quick Commands Cheatsheet

```bash
# Setup
setup.bat              # First-time setup (Windows)
pip install -r requirements.txt  # Manual setup

# Launch
start.bat              # Start app (Windows)
python sqlmap_gui/app.py  # Start app (all platforms)

# Demo
demo.bat               # API demo (Windows)
python demo_api.py     # API demo (all platforms)

# Access
http://localhost:5000  # Web interface
http://localhost:5000/api/health/features  # API health

# Login
admin / admin123       # Default credentials
```

---

**Ready to start? Run `start.bat` now!** 🚀

**SQLReaper v2.1 Advanced** | Built with 🔥 | Use Ethically
