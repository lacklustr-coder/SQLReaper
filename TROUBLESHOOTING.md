# SQLReaper Troubleshooting Guide

## 🔧 Batch File Closes Immediately

If `start.bat` opens and immediately closes, try these solutions:

### Solution 1: Use the Simple Launcher

```batch
start-simple.bat
```

This version has better error messages and won't close automatically.

### Solution 2: Use Debug Mode

```batch
start-debug.bat
```

This will run comprehensive tests and show you exactly where the problem is.

### Solution 3: Manual Start

```batch
# Open Command Prompt manually
# Navigate to SQLReaper directory
cd C:\path\to\SQLReaper

# Run directly
python sqlmap_gui\app.py
```

---

## 🐍 Python Issues

### Python Not Found

**Symptom:** "Python not found" or "python is not recognized"

**Solution:**
1. Install Python 3.8+ from https://www.python.org/downloads/
2. **Important:** Check "Add Python to PATH" during installation
3. Restart Command Prompt after installation
4. Test: `python --version`

### Wrong Python Version

**Symptom:** "Python 2.x" or version too old

**Solution:**
```batch
# Check version
python --version

# If wrong, try python3
python3 --version

# Update your PATH to use correct Python
```

---

## 📦 Dependency Issues

### Missing Dependencies

**Symptom:** "ModuleNotFoundError: No module named 'flask'"

**Solution:**
```batch
# Install dependencies
pip install -r requirements.txt

# If that fails, try with force reinstall
pip install -r requirements.txt --force-reinstall

# Or install individually
pip install flask werkzeug pystray Pillow flask-socketio python-socketio PyJWT
```

### PyJWT Import Error

**Symptom:** "No module named 'jwt'"

**Solution:**
```batch
# The package name is PyJWT, not jwt
pip install PyJWT
```

### Permission Errors During Install

**Symptom:** "Permission denied" or "Access is denied"

**Solution:**
```batch
# Run as administrator, or use --user flag
pip install -r requirements.txt --user
```

---

## 🌐 Port Issues

### Port 5000 Already in Use

**Symptom:** "Address already in use" or "Port 5000 is busy"

**Solution:**

**Option 1 - Find and Kill Process (Windows):**
```batch
# Find what's using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

**Option 2 - Use Different Port:**
Edit `sqlmap_gui\app.py` and change:
```python
# Find this line near the end
app.run(host="0.0.0.0", port=5000, debug=False)

# Change to:
app.run(host="0.0.0.0", port=8080, debug=False)
```

---

## 💾 Database Issues

### Database Locked or Corrupt

**Symptom:** "Database is locked" or SQLite errors

**Solution:**
```batch
# Delete the database (it will be recreated)
del sqlmap_gui\scans.db

# Restart the app
start.bat
```

### Permission Errors

**Symptom:** "Permission denied" when creating database

**Solution:**
```batch
# Run Command Prompt as Administrator
# Or check folder permissions

# Make sure these directories exist and are writable
mkdir results
mkdir profiles
mkdir uploads
```

---

## 🔌 Import Errors

### Cannot Import App Modules

**Symptom:** "ModuleNotFoundError: No module named 'database'" or similar

**Solution:**
```batch
# Make sure you're in the SQLReaper directory
cd C:\path\to\SQLReaper

# Not in sqlmap_gui directory!
# Run from parent directory

# Correct:
python sqlmap_gui\app.py

# Incorrect:
cd sqlmap_gui
python app.py  # This won't work!
```

---

## 🌐 Browser Issues

### Cannot Access http://localhost:5000

**Symptom:** "Can't reach this page" or "Connection refused"

**Solutions:**

1. **Check if server is actually running**
   - Look for "Running on http://..." in the console
   - Should say "Press Ctrl+C to stop"

2. **Try different URLs:**
   ```
   http://localhost:5000
   http://127.0.0.1:5000
   http://0.0.0.0:5000
   ```

3. **Check firewall:**
   - Windows Firewall may be blocking port 5000
   - Allow Python through firewall

4. **Check antivirus:**
   - Some antivirus software blocks Flask apps
   - Temporarily disable or add exception

---

## 🔐 Authentication Issues

### Cannot Login

**Symptom:** "Invalid credentials" with admin/admin123

**Solution:**
```batch
# The default credentials are case-sensitive:
Username: admin
Password: admin123

# If you changed the password and forgot it:
# Delete the database to reset
del sqlmap_gui\scans.db
```

---

## 🚀 Performance Issues

### App Starts Very Slowly

**Solutions:**

1. **Disable antivirus scanning for the directory**
2. **Check disk space** - SQLite needs space
3. **Update Python packages:**
   ```batch
   pip install --upgrade pip
   pip install -r requirements.txt --upgrade
   ```

### High CPU Usage

**Solutions:**

1. **Check for infinite loops in scans**
2. **Reduce concurrent scans in queue**
3. **Increase rate limiting delays**

---

## 📝 Common Error Messages

### "No module named 'enhancements'"

**Solution:**
```batch
# The file exists, Python can't find it
# Make sure you're running from SQLReaper directory, not sqlmap_gui
cd C:\path\to\SQLReaper
python sqlmap_gui\app.py
```

### "AttributeError: module 'werkzeug' has no attribute..."

**Solution:**
```batch
# Werkzeug version incompatibility
pip install werkzeug==3.0.0 --force-reinstall
```

### "RuntimeError: Working outside of application context"

**Solution:**
This is normal during startup if you see it briefly. If it persists, there's an initialization issue.

---

## 🔍 Debug Mode

To see all errors in detail:

```batch
# Run with Python's verbose mode
python -u sqlmap_gui\app.py

# Or set Flask debug mode
set FLASK_DEBUG=1
python sqlmap_gui\app.py
```

---

## 📊 Still Not Working?

### Collect Debug Information

Run `start-debug.bat` and save the output:

```batch
start-debug.bat > debug-output.txt
```

### Check These Files

1. **requirements.txt** - Should list all dependencies
2. **sqlmap_gui\app.py** - Main application file
3. **sqlmap_gui\init_features.py** - Feature initialization

### System Information to Collect

```batch
# Python version
python --version

# Pip version
pip --version

# Installed packages
pip list

# Current directory
cd

# Directory contents
dir sqlmap_gui
```

---

## ✅ Quick Checklist

Before asking for help, verify:

- [ ] Python 3.8+ is installed
- [ ] Python is in PATH (can run `python --version`)
- [ ] All dependencies are installed (`pip install -r requirements.txt`)
- [ ] You're in the SQLReaper directory (not sqlmap_gui)
- [ ] Port 5000 is available
- [ ] Antivirus isn't blocking Python
- [ ] You have write permissions in the directory

---

## 🆘 Getting Help

If none of these solutions work:

1. **Run `start-debug.bat`** and save the full output
2. **Check if the issue is already documented** in GitHub Issues
3. **Provide system information:**
   - Windows/Linux/Mac version
   - Python version
   - Full error message
   - What you've already tried

---

**Most Common Fix:**

90% of issues are solved by:

```batch
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Use simple launcher
start-simple.bat
```

Good luck! 🚀
