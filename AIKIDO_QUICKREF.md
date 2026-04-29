# 🛡️ Aikido Quick Reference Card

## Installation

```bash
# Aikido CLI
npm install -g @aikidosec/cli
# OR
pip install aikido-cli

# Dependencies (with lockfile)
pip install -r requirements-lock.txt
```

## Common Commands

### Scanning
```bash
aikido scan dependencies          # Quick dependency scan
aikido scan --all                 # Full security scan
aikido scan secrets               # Secrets detection only
aikido scan sast                  # Code analysis only
aikido scan --config aikido.yml   # Custom config scan
```

### Interactive Menu
```bash
aikido-scan.bat                   # Windows
./aikido-scan.sh                  # Linux/Mac
```

### Dependency Management
```bash
# Install
pip install -r requirements-lock.txt

# Update single package
pip install --upgrade package-name
pip freeze > requirements-lock.txt

# Update all
pip install -r requirements.txt --upgrade
pip freeze > requirements-lock.txt
```

## File Locations

```
SQLReaper/
├── aikido.yml                    # Main config
├── .aikidoignore                 # Scan exclusions
├── requirements-lock.txt         # Locked dependencies
├── aikido-scan.bat/.sh          # Interactive scanner
├── SECURITY.md                   # Security policy
├── AIKIDO_SETUP.md              # Setup guide
├── AIKIDO_INTEGRATION.md        # Integration docs
└── .github/workflows/
    └── aikido-security.yml      # CI/CD workflow
```

## Configuration Snippets

### Ignore Vulnerability
```yaml
# aikido.yml
vulnerabilities:
  ignore:
    - CVE-2024-12345
      reason: "Not applicable"
```

### Adjust Severity
```yaml
# aikido.yml
vulnerabilities:
  min_severity: high  # critical, high, medium, low, info
```

### Scan Timeout
```yaml
# aikido.yml
performance:
  timeout: 1200  # seconds
```

## GitHub Setup

1. Get token: [app.aikido.dev](https://app.aikido.dev/) → Settings → API Tokens
2. Add secret: Repo → Settings → Secrets → `AIKIDO_API_TOKEN`
3. Push to trigger scan

## Manual Workflow Trigger

1. GitHub → Actions
2. "Aikido Security Scan"
3. Run workflow

## View Results

- **Aikido Dashboard**: [app.aikido.dev](https://app.aikido.dev/)
- **GitHub Security**: Repo → Security → Code scanning
- **PR Comments**: Automatic on pull requests

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API token not found | Add `AIKIDO_API_TOKEN` to GitHub Secrets |
| Requirements not found | Commit `requirements-lock.txt` |
| Scan timeout | Increase timeout in `aikido.yml` |
| Too many vulns | Update deps or set `min_severity: high` |
| False positive | Add to ignore list in `aikido.yml` |

## Support

- Docs: [docs.aikido.dev](https://docs.aikido.dev/)
- Email: support@aikido.dev
- Discord: [discord.gg/aikido](https://discord.gg/aikido)

---

**Quick Start:** `aikido-scan.bat` or `./aikido-scan.sh`
