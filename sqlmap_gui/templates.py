"""
Scan templates for pre-configured scan types
"""

import uuid

from database import TemplateDB


def init_default_templates():
    """Initialize default scan templates"""

    templates = [
        {
            "id": "basic-detection",
            "name": "⚡ Basic Detection",
            "type": "basic",
            "description": "Quick vulnerability check - perfect for initial testing (2-3 min)",
            "options": {
                "level": "1",
                "risk": "1",
                "threads": "5",
                "technique": "BE",
                "batch": True,
            },
            "is_default": True,
            "icon": "⚡",
            "color": "#59C2FF",
        },
        {
            "id": "aggressive-full",
            "name": "🔥 Aggressive Full Scan",
            "type": "aggressive",
            "description": "Maximum coverage with all techniques - comprehensive testing (15-30 min)",
            "options": {
                "level": "5",
                "risk": "3",
                "threads": "4",
                "technique": "BEUSTQ",
                "batch": True,
                "getDbs": True,
                "getTables": True,
                "getColumns": True,
            },
            "is_default": True,
            "icon": "🔥",
            "color": "#FFB454",
        },
        {
            "id": "ninja-stealth",
            "name": "🥷 Ninja Stealth",
            "type": "stealth",
            "description": "Low and slow - avoid IDS/IPS/WAF detection (10-20 min)",
            "options": {
                "level": "2",
                "risk": "1",
                "threads": "1",
                "delay": "4",
                "timeout": "45",
                "retries": "3",
                "randomAgent": True,
                "batch": True,
                "technique": "BE",
            },
            "is_default": True,
            "icon": "🥷",
            "color": "#BAE67E",
        },
        {
            "id": "db-extraction",
            "name": "💾 Database Extraction",
            "type": "extraction",
            "description": "Full database dump - extract all tables and data (20-60 min)",
            "options": {
                "level": "3",
                "risk": "2",
                "threads": "3",
                "getDbs": True,
                "getTables": True,
                "getColumns": True,
                "dumpAll": True,
                "batch": True,
                "technique": "BEUST",
            },
            "is_default": True,
            "icon": "💾",
            "color": "#D4BFFF",
        },
        {
            "id": "waf-evasion",
            "name": "🛡️ WAF Evasion Master",
            "type": "waf_bypass",
            "description": "Advanced WAF bypass with multiple tamper scripts (10-25 min)",
            "options": {
                "level": "4",
                "risk": "3",
                "threads": "2",
                "tamper": "between,randomcase,space2comment,charencode",
                "randomAgent": True,
                "delay": "2",
                "batch": True,
                "technique": "BEUST",
                "timeout": "40",
            },
            "is_default": True,
            "icon": "🛡️",
            "color": "#F28779",
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
