# 🛡️ Aikido Security Setup Guide

Quick guide to get Aikido security scanning working with SQLReaper.

## Prerequisites

- Aikido account (free tier available at [aikido.dev](https://www.aikido.dev/))
- GitHub repository (for CI/CD integration)
- Python 3.8+

## Setup Steps

### 1. Create Aikido Account

1. Visit [https://app.aikido.dev/signup](https://app.aikido.dev/signup)
2. Sign up with GitHub or email
3. Create a new project or organization

### 2. Get API Token

1. Go to Aikido Dashboard → Settings → API Tokens
2. Click "Generate New Token"
3. Name it: `SQLReaper-GitHub-Actions`
4. Copy the token (you won't see it again!)

### 3. Configure GitHub Repository

1. Go to your GitHub repo → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add secret:
   - **Name**: `AIKIDO_API_TOKEN`
   - **Value**: Paste your Aikido API token
4. Click "Add secret"

### 4. Install Dependencies Locally

```bash
cd SQLReaper

# Install from lockfile for reproducible builds
pip install -r requirements-lock.txt

# Or install from requirements.txt
pip install -r requirements.txt
```

### 5. Install Aikido CLI (Optional for Local Scans)

```bash
# Using npm
npm install -g @aikidosec/cli

# Or using pip
pip install aikido-cli

# Verify installation
aikido --version
```

### 6. Configure Aikido CLI

```bash
# Login to Aikido
aikido login

# Follow the prompts to authenticate
```

### 7. Run Your First Scan

```bash
# Quick dependency scan
aikido scan dependencies

# Full security scan
aikido scan --all

# Scan with custom config
aikido scan --config aikido.yml
```

## Configuration Files

### `aikido.yml`

Main configuration file. Key sections:

```yaml
scan:
  dependencies: true  # Scan Python packages
  sast: true         # Static code analysis
  secrets: true      # Detect leaked secrets

python:
  requirements_file: requirements-lock.txt
  version: "3.8+"
  package_manager: pip
```

### `.aikidoignore`

Files/directories to exclude from scanning:

```
__pycache__/
venv/
results/
uploads/
*.md
```

### `requirements-lock.txt`

Locked dependency versions for:
- Reproducible builds
- Accurate vulnerability tracking
- Easy rollback

## GitHub Actions Workflow

The workflow (`.github/workflows/aikido-security.yml`) runs on:

- ✅ Push to `main`, `master`, `develop`
- ✅ Pull requests
- ✅ Weekly schedule (Mondays 9 AM UTC)
- ✅ Manual trigger

### Manual Trigger

1. Go to Actions tab in GitHub
2. Select "Aikido Security Scan"
3. Click "Run workflow"
4. Choose branch and run

## Viewing Results

### In Aikido Dashboard

1. Go to [https://app.aikido.dev/](https://app.aikido.dev/)
2. Select your project
3. View:
   - Vulnerabilities by severity
   - Dependency graph
   - Code security issues
   - Compliance reports

### In GitHub

1. Go to Security tab
2. Click "Code scanning"
3. View Aikido findings with line numbers
4. Create issues from findings

### In PR Comments

Aikido automatically comments on PRs with:
- Number of vulnerabilities found
- Severity breakdown
- Links to detailed reports

## Common Tasks

### Update a Vulnerable Dependency

```bash
# Check which package is vulnerable
aikido scan dependencies

# Update specific package
pip install --upgrade vulnerable-package

# Update lockfile
pip freeze > requirements-lock.txt

# Verify fix
aikido scan dependencies
```

### Add Dependency

```bash
# Install new package
pip install new-package

# Update requirements.txt
echo "new-package>=1.0.0" >> requirements.txt

# Update lockfile
pip freeze > requirements-lock.txt

# Scan for vulnerabilities
aikido scan dependencies
```

### Ignore False Positives

Edit `aikido.yml`:

```yaml
vulnerabilities:
  ignore:
    - CVE-2024-12345  # Add CVE to ignore
      reason: "False positive - not applicable to our usage"
```

### Customize Scan Paths

Edit `aikido.yml`:

```yaml
paths:
  include:
    - "sqlmap_gui/**/*.py"
    - "*.py"
  exclude:
    - "tests/**"
    - "temp/**"
```

## Troubleshooting

### "No API token found"

**Solution**: Make sure `AIKIDO_API_TOKEN` is set in GitHub Secrets.

### "Requirements file not found"

**Solution**: Ensure `requirements-lock.txt` exists in repo root:

```bash
pip freeze > requirements-lock.txt
git add requirements-lock.txt
git commit -m "Add requirements lockfile"
```

### "Scan timeout"

**Solution**: Increase timeout in `aikido.yml`:

```yaml
performance:
  timeout: 1200  # Increase to 20 minutes
```

### "Too many vulnerabilities"

**Solution**: 

1. Update dependencies:
   ```bash
   pip install -r requirements.txt --upgrade
   pip freeze > requirements-lock.txt
   ```

2. Or adjust severity threshold:
   ```yaml
   vulnerabilities:
     min_severity: high  # Only show high/critical
   ```

## Best Practices

### ✅ DO

- Run local scans before pushing
- Use `requirements-lock.txt` for installations
- Keep dependencies updated regularly
- Review all security findings
- Document ignored vulnerabilities

### ❌ DON'T

- Commit API keys or secrets
- Ignore critical vulnerabilities
- Disable security scans without reason
- Use outdated packages unnecessarily
- Skip dependency lockfile

## Support

### Aikido Support

- Documentation: [https://docs.aikido.dev/](https://docs.aikido.dev/)
- Community: [Aikido Discord](https://discord.gg/aikido)
- Email: support@aikido.dev

### SQLReaper Issues

- GitHub Issues: [Your repo]/issues
- Security: See `SECURITY.md`

## Next Steps

1. ✅ Complete setup steps above
2. ✅ Run first local scan
3. ✅ Push code to trigger CI/CD scan
4. ✅ Review findings in Aikido dashboard
5. ✅ Fix any critical/high vulnerabilities
6. ✅ Set up notifications (email/Slack)

---

🎉 **You're all set!** Aikido will now automatically scan your code for security issues.
