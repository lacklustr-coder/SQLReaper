"""
AI-Powered Vulnerability Analysis Engine
Pattern recognition, severity scoring, and automated remediation suggestions
"""

import re
from typing import Dict, List, Optional, Tuple


class VulnerabilityAnalyzer:
    """AI-powered vulnerability analysis and classification"""

    # Vulnerability patterns and signatures
    SQLI_PATTERNS = {
        "error_based": [
            r"SQL syntax.*?error",
            r"mysql_fetch",
            r"Warning.*?mysql_",
            r"valid MySQL result",
            r"MySqlClient\.",
            r"PostgreSQL.*?ERROR",
            r"ORA-\d{5}",
            r"Microsoft SQL Server",
        ],
        "blind_boolean": [
            r"true.*?false",
            r"1=1.*?1=2",
            r"and.*?or",
            r"response time differs",
        ],
        "time_based": [
            r"sleep\(\d+\)",
            r"benchmark\(",
            r"pg_sleep\(",
            r"waitfor delay",
        ],
        "union_based": [
            r"UNION.*?SELECT",
            r"ORDER BY \d+",
            r"NULL.*?NULL.*?NULL",
        ],
    }

    CRITICAL_INDICATORS = [
        "remote code execution",
        "system command",
        "file upload",
        "arbitrary file read",
        "privilege escalation",
        "authentication bypass",
        "session hijacking",
    ]

    HIGH_INDICATORS = [
        "sql injection",
        "union select",
        "database dump",
        "password hash",
        "admin panel",
        "xss",
        "csrf",
    ]

    MEDIUM_INDICATORS = [
        "information disclosure",
        "error message",
        "version detection",
        "banner grab",
        "directory listing",
    ]

    @staticmethod
    def analyze_injection_type(response: str, payload: str) -> Dict:
        """Analyze SQLi response and determine injection type"""
        injection_types = []
        confidence = 0

        for inj_type, patterns in VulnerabilityAnalyzer.SQLI_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, response, re.IGNORECASE):
                    injection_types.append(inj_type)
                    confidence += 15
                    break

        return {
            "injection_types": list(set(injection_types)),
            "confidence": min(confidence, 100),
            "analysis": VulnerabilityAnalyzer._generate_analysis(injection_types),
        }

    @staticmethod
    def _generate_analysis(injection_types: List[str]) -> str:
        """Generate detailed analysis based on injection types"""
        if not injection_types:
            return "No clear SQL injection pattern detected"

        analyses = []
        if "error_based" in injection_types:
            analyses.append(
                "Error-based SQLi detected - Database errors are being returned, allowing data extraction through error messages"
            )
        if "union_based" in injection_types:
            analyses.append(
                "UNION-based SQLi detected - Can extract data directly through UNION queries"
            )
        if "blind_boolean" in injection_types:
            analyses.append(
                "Boolean-based blind SQLi detected - Can infer data through true/false responses"
            )
        if "time_based" in injection_types:
            analyses.append(
                "Time-based blind SQLi detected - Can extract data through response delays"
            )

        return ". ".join(analyses)

    @staticmethod
    def calculate_severity(
        vuln_type: str, impact: str, exploitability: str, context: Dict
    ) -> Tuple[str, int, str]:
        """
        Calculate vulnerability severity using CVSS-like scoring
        Returns: (severity_label, score, justification)
        """
        base_score = 0
        factors = []

        # Base score by vulnerability type
        type_scores = {
            "sqli": 7.5,
            "rce": 9.5,
            "auth_bypass": 8.5,
            "xss": 6.0,
            "lfi": 7.0,
            "rfi": 8.5,
            "xxe": 7.5,
            "ssrf": 7.0,
            "nosqli": 7.5,
            "ldapi": 7.0,
            "command_injection": 9.0,
        }

        base_score = type_scores.get(vuln_type.lower(), 5.0)
        factors.append(f"Base vulnerability type: {vuln_type}")

        # Impact modifier
        impact_modifiers = {"high": 1.5, "medium": 1.0, "low": 0.7}
        impact_mod = impact_modifiers.get(impact.lower(), 1.0)
        base_score *= impact_mod
        factors.append(f"Impact level: {impact} (×{impact_mod})")

        # Exploitability modifier
        exploit_modifiers = {"easy": 1.3, "medium": 1.0, "hard": 0.8}
        exploit_mod = exploit_modifiers.get(exploitability.lower(), 1.0)
        base_score *= exploit_mod
        factors.append(f"Exploitability: {exploitability} (×{exploit_mod})")

        # Context adjustments
        if context.get("authenticated"):
            base_score *= 0.9
            factors.append("Requires authentication (×0.9)")

        if context.get("public_facing"):
            base_score *= 1.2
            factors.append("Public-facing endpoint (×1.2)")

        if context.get("admin_panel"):
            base_score *= 1.3
            factors.append("Admin panel access (×1.3)")

        if context.get("data_sensitive"):
            base_score *= 1.2
            factors.append("Sensitive data exposure (×1.2)")

        # Cap at 10.0
        final_score = min(base_score, 10.0)

        # Determine severity label
        if final_score >= 9.0:
            severity = "CRITICAL"
        elif final_score >= 7.0:
            severity = "HIGH"
        elif final_score >= 4.0:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        justification = " | ".join(factors) + f" → Final: {final_score:.1f}/10.0"

        return severity, round(final_score, 1), justification

    @staticmethod
    def generate_remediation(vuln_type: str, context: Dict) -> Dict:
        """Generate automated remediation suggestions"""
        remediations = {
            "sqli": {
                "immediate": [
                    "Use parameterized queries (prepared statements) instead of string concatenation",
                    "Implement input validation and sanitization",
                    "Apply principle of least privilege to database accounts",
                ],
                "short_term": [
                    "Deploy Web Application Firewall (WAF) with SQLi rules",
                    "Enable database query logging and monitoring",
                    "Implement rate limiting on suspicious query patterns",
                ],
                "long_term": [
                    "Code review all database interaction points",
                    "Implement ORM layer for database access",
                    "Regular security audits and penetration testing",
                    "Security training for development team",
                ],
                "code_example": """
# ❌ VULNERABLE
query = "SELECT * FROM users WHERE id = '" + user_id + "'"
cursor.execute(query)

# ✅ SECURE (Parameterized)
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))

# ✅ SECURE (ORM)
user = User.objects.get(id=user_id)
                """,
            },
            "rce": {
                "immediate": [
                    "Disable/remove vulnerable code immediately",
                    "Implement strict input validation whitelist",
                    "Never pass user input directly to system commands",
                ],
                "short_term": [
                    "Use safe APIs instead of shell commands",
                    "Run application with minimal privileges",
                    "Deploy intrusion detection system",
                ],
                "long_term": [
                    "Containerize application with restricted capabilities",
                    "Implement mandatory access control (SELinux/AppArmor)",
                    "Regular vulnerability scanning",
                ],
                "code_example": """
# ❌ VULNERABLE
os.system('ping ' + user_input)

# ✅ SECURE
import subprocess
subprocess.run(['ping', '-c', '4', validated_ip], capture_output=True)
                """,
            },
            "xss": {
                "immediate": [
                    "Implement output encoding for all user-controlled data",
                    "Set Content-Security-Policy headers",
                    "Use HTTPOnly and Secure flags on cookies",
                ],
                "short_term": [
                    "Deploy XSS protection headers (X-XSS-Protection)",
                    "Implement input validation on client and server",
                    "Use templating engines with auto-escaping",
                ],
                "long_term": [
                    "Security code review for all output points",
                    "Implement Content Security Policy reporting",
                    "Regular XSS scanning in CI/CD pipeline",
                ],
                "code_example": """
# ❌ VULNERABLE
html = "<div>" + user_input + "</div>"

# ✅ SECURE (Python/Flask)
from markupsafe import escape
html = "<div>" + escape(user_input) + "</div>"

# ✅ SECURE (JavaScript)
element.textContent = userInput;  // Not innerHTML
                """,
            },
        }

        # Get remediation or use default
        remediation = remediations.get(
            vuln_type.lower(),
            {
                "immediate": ["Patch immediately", "Validate all inputs"],
                "short_term": ["Review code", "Add monitoring"],
                "long_term": ["Security audit", "Team training"],
                "code_example": "// Contact security team for specific guidance",
            },
        )

        # Add context-specific suggestions
        if context.get("framework"):
            remediation["framework_specific"] = (
                f"Review {context['framework']} security best practices"
            )

        return remediation

    @staticmethod
    def detect_waf(response_headers: Dict, response_body: str) -> Optional[Dict]:
        """Detect Web Application Firewall from response"""
        waf_signatures = {
            "Cloudflare": [
                r"cloudflare",
                r"cf-ray",
                r"__cfduid",
                r"Attention Required! | Cloudflare",
            ],
            "AWS WAF": [r"x-amzn-requestid", r"x-amz-cf-id"],
            "Akamai": [r"akamai", r"AkamaiGHost"],
            "ModSecurity": [r"mod_security", r"NOYB"],
            "Imperva": [r"imperva", r"incapsula"],
            "Fortinet": [r"fortigate", r"fortiweb"],
            "F5 BIG-IP": [r"BigIP", r"F5", r"BIGipServer"],
            "Sucuri": [r"sucuri", r"cloudproxy"],
        }

        detected_wafs = []

        # Check headers
        header_str = str(response_headers).lower()
        for waf_name, signatures in waf_signatures.items():
            for sig in signatures:
                if re.search(sig, header_str, re.IGNORECASE):
                    detected_wafs.append(waf_name)
                    break

        # Check body
        for waf_name, signatures in waf_signatures.items():
            for sig in signatures:
                if re.search(sig, response_body, re.IGNORECASE):
                    if waf_name not in detected_wafs:
                        detected_wafs.append(waf_name)
                    break

        if detected_wafs:
            return {
                "detected": True,
                "wafs": detected_wafs,
                "bypass_suggestions": VulnerabilityAnalyzer._waf_bypass_suggestions(
                    detected_wafs
                ),
            }

        return {"detected": False, "wafs": [], "bypass_suggestions": []}

    @staticmethod
    def _waf_bypass_suggestions(wafs: List[str]) -> List[str]:
        """Generate WAF bypass suggestions"""
        suggestions = [
            "Use case-mix obfuscation (uNiOn SeLeCt)",
            "Try comment-based obfuscation (UN/**/ION SE/**/LECT)",
            "Use encoding (URL, Unicode, Hex)",
            "Try alternative syntax (UNION ALL SELECT)",
            "Use tamper scripts from sqlmap",
            "Implement time delays between requests",
            "Rotate User-Agents and IP addresses",
            "Fragment payloads across multiple parameters",
        ]

        # Add WAF-specific suggestions
        if "Cloudflare" in wafs:
            suggestions.extend(
                [
                    "Try targeting origin IP if exposed",
                    "Use rare User-Agents to avoid rate limiting",
                    "Implement exponential backoff on blocks",
                ]
            )

        if "ModSecurity" in wafs:
            suggestions.extend(
                [
                    "Check for paranoia level misconfigurations",
                    "Try HPP (HTTP Parameter Pollution)",
                    "Use NULL bytes in payloads",
                ]
            )

        return suggestions[:10]  # Return top 10

    @staticmethod
    def analyze_exploitation_chain(vulnerabilities: List[Dict]) -> Dict:
        """Analyze multiple vulnerabilities for chaining opportunities"""
        chains = []

        # Look for complementary vulnerabilities
        vuln_types = {v["type"]: v for v in vulnerabilities}

        # SQLi + File Read = Database + Source Code
        if "sqli" in vuln_types and "lfi" in vuln_types:
            chains.append(
                {
                    "name": "Database + Source Disclosure",
                    "vulns": ["sqli", "lfi"],
                    "impact": "CRITICAL",
                    "description": "Combine SQLi to read file paths from DB, then use LFI to read source code",
                    "steps": [
                        "Use SQLi to enumerate database and find file paths",
                        "Extract configuration file paths and credentials",
                        "Use LFI to read application source code",
                        "Find additional vulnerabilities in source",
                    ],
                }
            )

        # SQLi + Upload = Shell Upload
        if "sqli" in vuln_types and "file_upload" in vuln_types:
            chains.append(
                {
                    "name": "SQL to Shell Upload",
                    "vulns": ["sqli", "file_upload"],
                    "impact": "CRITICAL",
                    "description": "Use SQLi to bypass upload restrictions and upload web shell",
                    "steps": [
                        "Use SQLi to modify file upload whitelist in database",
                        "Upload malicious file (web shell)",
                        "Execute commands through web shell",
                    ],
                }
            )

        # XSS + CSRF = Account Takeover
        if "xss" in vuln_types and "csrf" in vuln_types:
            chains.append(
                {
                    "name": "XSS + CSRF Account Takeover",
                    "vulns": ["xss", "csrf"],
                    "impact": "HIGH",
                    "description": "Use XSS to execute CSRF attack for account takeover",
                    "steps": [
                        "Inject XSS payload to capture session token",
                        "Use CSRF to change account credentials",
                        "Leverage elevated privileges",
                    ],
                }
            )

        return {
            "chains_found": len(chains),
            "chains": chains,
            "recommendation": "Prioritize fixing these vulnerabilities as they can be chained for higher impact",
        }

    @staticmethod
    def predict_next_steps(current_findings: List[Dict]) -> List[Dict]:
        """AI-powered prediction of next penetration testing steps"""
        suggestions = []

        # Analyze current findings
        has_sqli = any(v.get("type") == "sqli" for v in current_findings)
        has_auth = any("auth" in str(v).lower() for v in current_findings)
        has_admin = any("admin" in str(v).lower() for v in current_findings)

        if has_sqli:
            suggestions.extend(
                [
                    {
                        "action": "Enumerate Database",
                        "priority": "HIGH",
                        "command": "--dbs --tables --columns",
                        "reason": "SQLi found - enumerate database structure",
                    },
                    {
                        "action": "Dump Credentials",
                        "priority": "CRITICAL",
                        "command": "--dump -T users",
                        "reason": "Extract user credentials for privilege escalation",
                    },
                    {
                        "action": "Check File Read",
                        "priority": "MEDIUM",
                        "command": "--file-read=/etc/passwd",
                        "reason": "Test for arbitrary file read capability",
                    },
                ]
            )

        if has_auth:
            suggestions.extend(
                [
                    {
                        "action": "Test Session Management",
                        "priority": "HIGH",
                        "command": "Test session fixation and hijacking",
                        "reason": "Auth mechanism found - test session security",
                    }
                ]
            )

        if has_admin:
            suggestions.extend(
                [
                    {
                        "action": "Admin Function Enumeration",
                        "priority": "CRITICAL",
                        "command": "Map all admin functionality",
                        "reason": "Admin panel access - enumerate privileged functions",
                    }
                ]
            )

        # Default reconnaissance
        if not current_findings:
            suggestions.extend(
                [
                    {
                        "action": "Basic Reconnaissance",
                        "priority": "HIGH",
                        "command": "Run discovery scan with --batch --crawl=3",
                        "reason": "No findings yet - perform initial reconnaissance",
                    }
                ]
            )

        return sorted(
            suggestions,
            key=lambda x: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}[
                x["priority"]
            ],
        )
