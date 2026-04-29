"""
Scan templates for pre-configured scan types
"""

import uuid

from database import TemplateDB


def init_default_templates():
    """Initialize default scan templates"""

    templates = [
        {
            "id": "quick-scan",
            "name": "Quick Scan",
            "type": "quick",
            "description": "Fast scan with basic detection",
            "options": {
                "level": "1",
                "risk": "1",
                "threads": "5",
                "technique": "BEUST",
                "batch": True,
            },
            "is_default": True,
        },
        {
            "id": "thorough-scan",
            "name": "Thorough Scan",
            "type": "thorough",
            "description": "Comprehensive scan with all tests",
            "options": {
                "level": "5",
                "risk": "3",
                "threads": "3",
                "technique": "BEUSTQ",
                "batch": True,
                "tamper": "space2comment",
            },
            "is_default": True,
        },
        {
            "id": "stealth-scan",
            "name": "Stealth Scan",
            "type": "stealth",
            "description": "Slow, stealthy scan to avoid detection",
            "options": {
                "level": "2",
                "risk": "1",
                "threads": "1",
                "delay": "3",
                "timeout": "30",
                "retries": "2",
                "randomAgent": True,
                "batch": True,
            },
            "is_default": True,
        },
        {
            "id": "enumeration-scan",
            "name": "Full Enumeration",
            "type": "enumeration",
            "description": "Extract all database information",
            "options": {
                "level": "3",
                "risk": "2",
                "getDbs": True,
                "getTables": True,
                "getColumns": True,
                "dumpAll": True,
                "batch": True,
            },
            "is_default": True,
        },
        {
            "id": "time-based-scan",
            "name": "Time-Based Blind",
            "type": "time_based",
            "description": "Focus on time-based blind injection",
            "options": {
                "level": "3",
                "risk": "2",
                "technique": "T",
                "timeSec": "10",
                "batch": True,
            },
            "is_default": False,
        },
        {
            "id": "union-scan",
            "name": "Union-Based",
            "type": "union",
            "description": "Focus on UNION query injection",
            "options": {
                "level": "3",
                "risk": "2",
                "technique": "U",
                "unionCols": "1-20",
                "batch": True,
            },
            "is_default": False,
        },
        {
            "id": "error-based-scan",
            "name": "Error-Based",
            "type": "error",
            "description": "Focus on error-based injection",
            "options": {
                "level": "3",
                "risk": "2",
                "technique": "E",
                "batch": True,
            },
            "is_default": False,
        },
        {
            "id": "waf-bypass-scan",
            "name": "WAF Bypass",
            "type": "waf_bypass",
            "description": "Scan with WAF bypass techniques",
            "options": {
                "level": "4",
                "risk": "3",
                "tamper": "between,randomcase,space2comment",
                "randomAgent": True,
                "delay": "2",
                "batch": True,
            },
            "is_default": False,
        },
    ]

    for template in templates:
        try:
            TemplateDB.create(
                template["id"],
                template["name"],
                template["type"],
                template["options"],
                template["description"],
                template["is_default"],
            )
        except:
            pass  # Already exists


def get_template(template_id: str):
    """Get template by ID"""
    return TemplateDB.get(template_id)


def get_all_templates():
    """Get all templates"""
    return TemplateDB.get_all()


def template_to_sqlmap_options(template: dict) -> list:
    """Convert template options to sqlmap command arguments"""
    options = template.get("options", {})
    args = []

    # Level and risk
    if "level" in options:
        args.extend(["--level", str(options["level"])])
    if "risk" in options:
        args.extend(["--risk", str(options["risk"])])

    # Techniques
    if "technique" in options:
        args.extend(["--technique", options["technique"]])

    # Performance
    if "threads" in options:
        args.extend(["--threads", str(options["threads"])])
    if "delay" in options:
        args.extend(["--delay", str(options["delay"])])
    if "timeout" in options:
        args.extend(["--timeout", str(options["timeout"])])
    if "retries" in options:
        args.extend(["--retries", str(options["retries"])])

    # Tamper scripts
    if "tamper" in options:
        args.extend(["--tamper", options["tamper"]])

    # Enumeration
    if options.get("getDbs"):
        args.append("--dbs")
    if options.get("getTables"):
        args.append("--tables")
    if options.get("getColumns"):
        args.append("--columns")
    if options.get("dumpAll"):
        args.append("--dump-all")

    # Misc
    if options.get("randomAgent"):
        args.append("--random-agent")
    if options.get("batch"):
        args.append("--batch")
    if "timeSec" in options:
        args.extend(["--time-sec", str(options["timeSec"])])
    if "unionCols" in options:
        args.extend(["--union-cols", options["unionCols"]])

    return args
