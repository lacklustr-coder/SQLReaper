"""
Advanced reporting module with PDF generation and statistics
"""

import io
import json
from datetime import datetime
from typing import Dict, List

from database import ScanDB, VulnerabilityDB


def generate_statistics() -> Dict:
    """Generate scan statistics"""
    all_scans = ScanDB.get_all(limit=1000)
    all_vulns = VulnerabilityDB.get_all(limit=1000)

    stats = {
        "total_scans": len(all_scans),
        "completed_scans": len([s for s in all_scans if s["status"] == "completed"]),
        "failed_scans": len(
            [s for s in all_scans if s["status"] in ["failed", "error"]]
        ),
        "running_scans": len([s for s in all_scans if s["status"] == "running"]),
        "total_vulnerabilities": len(all_vulns),
        "critical_vulns": len([v for v in all_vulns if v["severity"] == "critical"]),
        "high_vulns": len([v for v in all_vulns if v["severity"] == "high"]),
        "medium_vulns": len([v for v in all_vulns if v["severity"] == "medium"]),
        "low_vulns": len([v for v in all_vulns if v["severity"] == "low"]),
        "false_positives": len([v for v in all_vulns if v["false_positive"] == 1]),
        "vuln_types": {},
        "owasp_categories": {},
        "database_types": {},
        "scan_success_rate": 0.0,
    }

    # Count vulnerability types
    for vuln in all_vulns:
        vtype = vuln["vuln_type"]
        stats["vuln_types"][vtype] = stats["vuln_types"].get(vtype, 0) + 1

        if vuln["owasp_category"]:
            ocat = vuln["owasp_category"]
            stats["owasp_categories"][ocat] = stats["owasp_categories"].get(ocat, 0) + 1

        if vuln["database_type"]:
            dbtype = vuln["database_type"]
            stats["database_types"][dbtype] = stats["database_types"].get(dbtype, 0) + 1

    # Success rate
    if stats["total_scans"] > 0:
        stats["scan_success_rate"] = (
            stats["completed_scans"] / stats["total_scans"]
        ) * 100

    return stats


def generate_html_report(scan_id: str) -> str:
    """Generate HTML report for a scan"""
    scan = ScanDB.get(scan_id)
    if not scan:
        return "<html><body><h1>Scan not found</h1></body></html>"

    vulns = VulnerabilityDB.get_by_scan(scan_id)

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SQLReaper Scan Report - {scan["target"]}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 40px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: 200px 1fr;
            gap: 10px;
            margin: 20px 0;
        }}
        .info-label {{
            font-weight: bold;
            color: #555;
        }}
        .severity-critical {{
            background: #e74c3c;
            color: white;
            padding: 5px 10px;
            border-radius: 3px;
        }}
        .severity-high {{
            background: #e67e22;
            color: white;
            padding: 5px 10px;
            border-radius: 3px;
        }}
        .severity-medium {{
            background: #f39c12;
            color: white;
            padding: 5px 10px;
            border-radius: 3px;
        }}
        .severity-low {{
            background: #3498db;
            color: white;
            padding: 5px 10px;
            border-radius: 3px;
        }}
        .vuln-card {{
            border: 1px solid #ddd;
            margin: 20px 0;
            padding: 20px;
            border-radius: 5px;
            background: #fafafa;
        }}
        .vuln-title {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        pre {{
            background: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            text-align: center;
            color: #777;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>&#9760; SQLReaper Security Scan Report</h1>

        <h2>Scan Information</h2>
        <div class="info-grid">
            <div class="info-label">Target:</div>
            <div>{scan["target"]}</div>

            <div class="info-label">Scan ID:</div>
            <div>{scan["id"]}</div>

            <div class="info-label">Scan Type:</div>
            <div>{scan["scan_type"]}</div>

            <div class="info-label">Status:</div>
            <div>{scan["status"]}</div>

            <div class="info-label">Start Time:</div>
            <div>{scan["start_time"]}</div>

            <div class="info-label">End Time:</div>
            <div>{scan.get("end_time", "N/A")}</div>

            <div class="info-label">Vulnerabilities:</div>
            <div>{len(vulns)} found</div>
        </div>

        <h2>Vulnerabilities Found</h2>
"""

    if vulns:
        for vuln in vulns:
            severity_class = f"severity-{vuln['severity']}"
            html += f"""
        <div class="vuln-card">
            <div class="vuln-title">
                {vuln["vuln_type"].replace("_", " ").title()}
                <span class="{severity_class}">{vuln["severity"].upper()}</span>
            </div>
            <div class="info-grid">
                <div class="info-label">Parameter:</div>
                <div>{vuln.get("parameter", "N/A")}</div>

                <div class="info-label">Database:</div>
                <div>{vuln.get("database_type", "Unknown")}</div>

                <div class="info-label">OWASP:</div>
                <div>{vuln.get("owasp_category", "N/A")}</div>

                <div class="info-label">Description:</div>
                <div>{vuln.get("description", "N/A")}</div>
            </div>

            {f"<pre><code>{vuln["payload"]}</code></pre>" if vuln.get("payload") else ""}

            {f"<p><strong>Evidence:</strong><br>{vuln["evidence"]}</p>" if vuln.get("evidence") else ""}
        </div>
"""
    else:
        html += "<p>No vulnerabilities found.</p>"

    html += f"""
        <div class="footer">
            Generated by SQLReaper v2.1 on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </div>
    </div>
</body>
</html>
"""

    return html


def generate_markdown_report(scan_id: str) -> str:
    """Generate Markdown report for a scan"""
    scan = ScanDB.get(scan_id)
    if not scan:
        return "# Scan not found"

    vulns = VulnerabilityDB.get_by_scan(scan_id)

    md = f"""# SQLReaper Scan Report

## Scan Information

- **Target:** {scan["target"]}
- **Scan ID:** {scan["id"]}
- **Scan Type:** {scan["scan_type"]}
- **Status:** {scan["status"]}
- **Start Time:** {scan["start_time"]}
- **End Time:** {scan.get("end_time", "N/A")}
- **Vulnerabilities:** {len(vulns)} found

## Vulnerabilities

"""

    if vulns:
        for i, vuln in enumerate(vulns, 1):
            md += f"""
### {i}. {vuln["vuln_type"].replace("_", " ").title()} [{vuln["severity"].upper()}]

- **Parameter:** {vuln.get("parameter", "N/A")}
- **Database:** {vuln.get("database_type", "Unknown")}
- **OWASP Category:** {vuln.get("owasp_category", "N/A")}
- **Description:** {vuln.get("description", "N/A")}

"""
            if vuln.get("payload"):
                md += f"**Payload:**\n```\n{vuln['payload']}\n```\n\n"

            if vuln.get("evidence"):
                md += f"**Evidence:**\n```\n{vuln['evidence']}\n```\n\n"
    else:
        md += "No vulnerabilities found.\n"

    md += f"\n---\n*Generated by SQLReaper v2.1 on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"

    return md


def generate_json_report(scan_id: str) -> str:
    """Generate JSON report for a scan"""
    scan = ScanDB.get(scan_id)
    if not scan:
        return json.dumps({"error": "Scan not found"})

    vulns = VulnerabilityDB.get_by_scan(scan_id)

    report = {
        "scan": scan,
        "vulnerabilities": vulns,
        "summary": {
            "total_vulnerabilities": len(vulns),
            "by_severity": {
                "critical": len([v for v in vulns if v["severity"] == "critical"]),
                "high": len([v for v in vulns if v["severity"] == "high"]),
                "medium": len([v for v in vulns if v["severity"] == "medium"]),
                "low": len([v for v in vulns if v["severity"] == "low"]),
            },
        },
        "generated_at": datetime.now().isoformat(),
    }

    return json.dumps(report, indent=2, default=str)


def generate_csv_export(scans: List[Dict]) -> str:
    """Generate CSV export of scans"""
    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(
        [
            "ID",
            "Target",
            "Type",
            "Status",
            "Start Time",
            "End Time",
            "Exit Code",
            "Vulnerabilities",
        ]
    )

    for scan in scans:
        vulns = VulnerabilityDB.get_by_scan(scan["id"])
        writer.writerow(
            [
                scan["id"],
                scan["target"],
                scan["scan_type"],
                scan["status"],
                scan["start_time"],
                scan.get("end_time", ""),
                scan.get("exit_code", ""),
                len(vulns),
            ]
        )

    return output.getvalue()


def compare_scans(scan_id1: str, scan_id2: str) -> Dict:
    """Compare two scans to find differences"""
    scan1 = ScanDB.get(scan_id1)
    scan2 = ScanDB.get(scan_id2)

    if not scan1 or not scan2:
        return {"error": "One or both scans not found"}

    vulns1 = VulnerabilityDB.get_by_scan(scan_id1)
    vulns2 = VulnerabilityDB.get_by_scan(scan_id2)

    def vuln_key(v):
        return f"{v['vuln_type']}:{v.get('parameter', '')}:{v.get('payload', '')}"

    vulns1_keys = {vuln_key(v): v for v in vulns1}
    vulns2_keys = {vuln_key(v): v for v in vulns2}

    new_vulns = [vulns2_keys[k] for k in vulns2_keys if k not in vulns1_keys]
    fixed_vulns = [vulns1_keys[k] for k in vulns1_keys if k not in vulns2_keys]
    common_vulns = [vulns1_keys[k] for k in vulns1_keys if k in vulns2_keys]

    return {
        "scan1": scan1,
        "scan2": scan2,
        "new_vulnerabilities": new_vulns,
        "fixed_vulnerabilities": fixed_vulns,
        "common_vulnerabilities": common_vulns,
        "summary": {
            "new": len(new_vulns),
            "fixed": len(fixed_vulns),
            "common": len(common_vulns),
        },
    }
