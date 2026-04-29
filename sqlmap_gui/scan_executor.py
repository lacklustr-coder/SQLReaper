"""
Enhanced scan executor with WebSocket streaming and vulnerability detection
"""

import logging
import re
import subprocess
import threading
import time
import traceback
from datetime import datetime
from typing import Callable, Dict, List, Optional

from database import ErrorLogDB, ScanDB, ScriptDB, VulnerabilityDB
from websocket_manager import (
    emit_error,
    emit_scan_complete,
    emit_scan_output,
    emit_scan_status,
    emit_vulnerability_found,
)

logger = logging.getLogger(__name__)


class VulnerabilityParser:
    """Parse sqlmap output for vulnerabilities"""

    VULN_PATTERNS = {
        "sql_injection": r"Parameter: (.+?) \((.+?)\).*?Type: (.+?).*?Title: (.+?).*?Payload: (.+?)$",
        "database_detected": r"back-end DBMS: (.+?)$",
        "error_based": r"error-based",
        "time_based": r"time-based",
        "union_query": r"UNION query",
        "boolean_based": r"boolean-based blind",
        "stacked_queries": r"stacked queries",
    }

    @staticmethod
    def parse_output(output: str, scan_id: str, target: str) -> List[Dict]:
        """Extract vulnerabilities from sqlmap output"""
        vulnerabilities = []

        # SQL Injection detection
        for match in re.finditer(
            VulnerabilityParser.VULN_PATTERNS["sql_injection"],
            output,
            re.MULTILINE | re.DOTALL,
        ):
            parameter = match.group(1).strip()
            param_type = match.group(2).strip()
            technique = match.group(3).strip()
            title = match.group(4).strip()
            payload = match.group(5).strip()

            severity = VulnerabilityParser._determine_severity(technique, title)
            owasp = "A03:2021-Injection"

            vuln = {
                "scan_id": scan_id,
                "vuln_type": "sql_injection",
                "severity": severity,
                "parameter": parameter,
                "payload": payload,
                "description": title,
                "evidence": f"Type: {technique}\nParameter Type: {param_type}",
                "owasp_category": owasp,
            }
            vulnerabilities.append(vuln)

        # Database type detection
        db_match = re.search(
            VulnerabilityParser.VULN_PATTERNS["database_detected"], output
        )
        if db_match:
            db_type = db_match.group(1).strip()
            for vuln in vulnerabilities:
                vuln["database_type"] = db_type

        return vulnerabilities

    @staticmethod
    def _determine_severity(technique: str, title: str) -> str:
        """Determine vulnerability severity based on technique"""
        technique_lower = technique.lower()
        title_lower = title.lower()

        if "union" in technique_lower or "error" in technique_lower:
            return "critical"
        elif "time" in technique_lower or "boolean" in technique_lower:
            return "high"
        elif "stacked" in technique_lower:
            return "critical"
        else:
            return "medium"

    @staticmethod
    def detect_nosql_injection(output: str) -> Optional[Dict]:
        """Detect NoSQL injection indicators"""
        patterns = [
            r"\$ne|\$gt|\$lt|\$regex",
            r"MongoDB.*error",
            r"CouchDB.*error",
            r'\{"\$where"',
        ]

        for pattern in patterns:
            if re.search(pattern, output, re.IGNORECASE):
                return {
                    "vuln_type": "nosql_injection",
                    "severity": "high",
                    "owasp_category": "A03:2021-Injection",
                }
        return None

    @staticmethod
    def detect_command_injection(output: str) -> Optional[Dict]:
        """Detect command injection indicators"""
        patterns = [
            r"root:.*?:[0-9]+:[0-9]+:",  # /etc/passwd
            r"uid=\d+\(.*?\)\s+gid=\d+",  # id command
            r"total\s+\d+.*?drwx",  # ls -la
            r"<DIR>|Directory of",  # dir command
        ]

        for pattern in patterns:
            if re.search(pattern, output):
                return {
                    "vuln_type": "command_injection",
                    "severity": "critical",
                    "owasp_category": "A03:2021-Injection",
                }
        return None

    @staticmethod
    def detect_ldap_injection(output: str) -> Optional[Dict]:
        """Detect LDAP injection indicators"""
        patterns = [
            r"LDAP.*error",
            r"javax\.naming",
            r"ldap_bind|ldap_search",
        ]

        for pattern in patterns:
            if re.search(pattern, output, re.IGNORECASE):
                return {
                    "vuln_type": "ldap_injection",
                    "severity": "high",
                    "owasp_category": "A03:2021-Injection",
                }
        return None

    @staticmethod
    def detect_xxe(output: str) -> Optional[Dict]:
        """Detect XXE indicators"""
        patterns = [
            r"<!DOCTYPE.*?\[<!ENTITY",
            r"<!ENTITY.*?SYSTEM",
            r"XML.*?External.*?Entity",
        ]

        for pattern in patterns:
            if re.search(pattern, output, re.IGNORECASE):
                return {
                    "vuln_type": "xxe",
                    "severity": "high",
                    "owasp_category": "A05:2021-Security Misconfiguration",
                }
        return None

    @staticmethod
    def detect_ssrf(output: str) -> Optional[Dict]:
        """Detect SSRF indicators"""
        patterns = [
            r"http://169\.254\.169\.254",
            r"http://localhost:[0-9]+",
            r"http://127\.0\.0\.1",
            r"file:///etc/passwd",
        ]

        for pattern in patterns:
            if re.search(pattern, output):
                return {
                    "vuln_type": "ssrf",
                    "severity": "high",
                    "owasp_category": "A10:2021-Server-Side Request Forgery",
                }
        return None


def execute_scan(scan_data: Dict, callback: Optional[Callable[[bool], None]] = None):
    """
    Execute a scan with real-time output streaming and vulnerability detection
    """
    scan_id = scan_data["id"]
    target = scan_data["target"]
    options = scan_data.get("options", "")

    start_time = datetime.now()
    output_buffer = []

    try:
        # Run pre-scan scripts
        pre_scripts = ScriptDB.get_enabled("pre_scan")
        for script in pre_scripts:
            try:
                exec(script["code"], {"scan_data": scan_data, "logger": logger})
            except Exception as e:
                logger.error(f"Pre-scan script error: {e}")
                ErrorLogDB.create(
                    "script_error", str(e), scan_id, traceback.format_exc()
                )

        emit_scan_status(scan_id, "running", progress=0, details="Starting scan...")
        ScanDB.update_status(scan_id, "running")

        # Build command
        cmd = build_command(scan_data)
        logger.info(f"Executing: {' '.join(cmd)}")

        # Execute with real-time output
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
        )

        vulnerabilities_found = []

        # Stream output
        for line in iter(process.stdout.readline, ""):
            if line:
                output_buffer.append(line)
                emit_scan_output(scan_id, line, "stdout")

                # Parse for vulnerabilities in real-time
                combined = "".join(output_buffer[-50:])  # Last 50 lines

                # SQL Injection
                vulns = VulnerabilityParser.parse_output(combined, scan_id, target)
                for vuln in vulns:
                    # Check for duplicates
                    existing = VulnerabilityDB.deduplicate(
                        target, vuln["vuln_type"], vuln.get("parameter", "")
                    )
                    if not existing:
                        vuln_id = VulnerabilityDB.create(**vuln)
                        vuln["id"] = vuln_id
                        vulnerabilities_found.append(vuln)
                        emit_vulnerability_found(scan_id, vuln)

                # Other injection types
                for detector in [
                    VulnerabilityParser.detect_nosql_injection,
                    VulnerabilityParser.detect_command_injection,
                    VulnerabilityParser.detect_ldap_injection,
                    VulnerabilityParser.detect_xxe,
                    VulnerabilityParser.detect_ssrf,
                ]:
                    detected = detector(combined)
                    if detected:
                        detected["scan_id"] = scan_id
                        detected["parameter"] = "detected"
                        detected["description"] = f"{detected['vuln_type']} detected"
                        vuln_id = VulnerabilityDB.create(**detected)
                        detected["id"] = vuln_id
                        vulnerabilities_found.append(detected)
                        emit_vulnerability_found(scan_id, detected)

                # Progress estimation
                if "testing" in line.lower():
                    emit_scan_status(scan_id, "running", progress=30)
                elif "injectable" in line.lower():
                    emit_scan_status(scan_id, "running", progress=60)
                elif "dumping" in line.lower():
                    emit_scan_status(scan_id, "running", progress=80)

        # Get stderr
        stderr = process.stderr.read()
        if stderr:
            output_buffer.append(stderr)
            emit_scan_output(scan_id, stderr, "stderr")

        # Wait for completion
        exit_code = process.wait()

        # Complete
        end_time = datetime.now()
        duration = int((end_time - start_time).total_seconds())
        full_output = "".join(output_buffer)

        success = exit_code == 0
        ScanDB.update_status(
            scan_id,
            "completed" if success else "failed",
            exit_code,
            full_output,
            end_time.isoformat(),
        )

        emit_scan_complete(scan_id, success, exit_code, len(vulnerabilities_found))

        # Run post-scan scripts
        post_scripts = ScriptDB.get_enabled("post_scan")
        for script in post_scripts:
            try:
                exec(
                    script["code"],
                    {
                        "scan_data": scan_data,
                        "output": full_output,
                        "vulnerabilities": vulnerabilities_found,
                        "logger": logger,
                    },
                )
            except Exception as e:
                logger.error(f"Post-scan script error: {e}")
                ErrorLogDB.create(
                    "script_error", str(e), scan_id, traceback.format_exc()
                )

        if callback:
            callback(success)

        return success

    except Exception as e:
        logger.error(f"Scan execution error: {e}", exc_info=True)
        error_msg = str(e)
        ErrorLogDB.create("scan_error", error_msg, scan_id, traceback.format_exc())
        ScanDB.update_status(scan_id, "error", -1, error_msg)
        emit_error(scan_id, error_msg, "fatal")

        if callback:
            callback(False)

        return False


def build_command(scan_data: Dict) -> List[str]:
    """Build sqlmap command from scan data"""
    from app import load_settings

    settings = load_settings()
    sqlmap_path = settings.get("sqlmap_path", "")

    cmd = ["python", sqlmap_path, "-u", scan_data["target"]]

    # Add options
    if scan_data.get("options"):
        import shlex

        cmd.extend(shlex.split(scan_data["options"]))

    # Ensure batch mode
    if "--batch" not in cmd:
        cmd.append("--batch")

    return cmd
