# Security Policy

## 🛡️ Security Scanning with Aikido

This project uses [Aikido](https://www.aikido.dev/) for continuous security monitoring and vulnerability detection.

### What Aikido Scans

- **Dependency Vulnerabilities**: Monitors all Python packages in `requirements-lock.txt`
- **SAST (Static Analysis)**: Analyzes Python code for security issues
- **Secrets Detection**: Scans for accidentally committed API keys, tokens, passwords
- **Compliance Checks**: OWASP Top 10, CWE Top 25

### Configuration Files

- `aikido.yml` - Main Aikido configuration
- `.aikidoignore` - Files/directories excluded from scanning
- `requirements-lock.txt` - Locked dependencies for reproducible builds
- `.github/workflows/aikido-security.yml` - CI/CD integration

### Running Security Scans Locally

#### Install Aikido CLI

```bash
# Using npm
npm install -g @aikidosec/cli

# Or using pip
pip install aikido-cli
```

#### Run Local Scan

```bash
# Scan dependencies
aikido scan dependencies

# Full security scan
aikido scan --all

# Scan with custom config
aikido scan --config aikido.yml
```

### CI/CD Integration

Aikido automatically scans:
- Every push to `main`, `master`, or `develop` branches
- All pull requests
- Weekly scheduled scans (Mondays at 9 AM UTC)

#### Setup GitHub Actions

1. Get your API token from [Aikido Dashboard](https://app.aikido.dev/)
2. Add it to GitHub Secrets as `AIKIDO_API_TOKEN`:
   - Go to Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `AIKIDO_API_TOKEN`
   - Value: Your Aikido API token

### Dependency Management

#### Using Locked Dependencies

For reproducible builds and accurate vulnerability tracking:

```bash
# Install from lockfile
pip install -r requirements-lock.txt

# Update dependencies
pip install -r requirements.txt --upgrade
pip freeze > requirements-lock.txt
```

#### Updating Dependencies Safely

1. Check for vulnerabilities first:
   ```bash
   aikido scan dependencies
   ```

2. Update specific package:
   ```bash
   pip install --upgrade package-name
   pip freeze > requirements-lock.txt
   ```

3. Re-scan after updates:
   ```bash
   aikido scan dependencies
   ```

### Vulnerability Response

#### Critical/High Severity

1. **Automatic Alerts**: Team is notified via configured channels
2. **PR Blocking**: Critical vulnerabilities block PR merges
3. **Immediate Action**: Update affected dependencies within 24-48 hours

#### Medium/Low Severity

1. **Tracked**: Logged in Aikido dashboard
2. **Scheduled Fix**: Addressed in next sprint/release
3. **Risk Assessment**: Evaluated based on exposure and exploitability

### Custom Security Rules

The project has custom rules for penetration testing tools:

- ✅ **Subprocess Usage**: Allowed (required for sqlmap integration)
- ⚠️ **Dynamic Execution**: Warned (eval/exec used carefully in scan scenarios)

These are defined in `aikido.yml` under the `rules.custom` section.

### Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** open a public issue
2. Email: [Your security contact email]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We aim to respond within 48 hours.

### Security Best Practices

When contributing to SQLReaper:

- ✅ Use `requirements-lock.txt` for installations
- ✅ Never commit secrets or API keys
- ✅ Run local security scans before PR
- ✅ Keep dependencies updated
- ✅ Use environment variables for sensitive config
- ❌ Don't disable security warnings without review
- ❌ Don't ignore Aikido findings without justification

### Compliance

SQLReaper aims to comply with:

- **OWASP Top 10** - Web application security risks
- **CWE Top 25** - Most dangerous software weaknesses

Compliance reports are generated automatically and available in the Aikido dashboard.

### Resources

- [Aikido Documentation](https://docs.aikido.dev/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)

### Version History

- **v2.1** - Aikido integration added
- Initial security scanning enabled

---

**Note**: This is a penetration testing tool intended for authorized security testing only. Users are responsible for compliance with applicable laws and regulations.
