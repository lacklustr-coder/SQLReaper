"""
Extended API routes for new features
"""

import json
import uuid

from ai_analyzer import VulnerabilityAnalyzer
from database import (
    ErrorLogDB,
    PayloadDB,
    QueueDB,
    ScanDB,
    ScriptDB,
    TemplateDB,
    VulnerabilityDB,
)
from flask import Blueprint, Response, jsonify, request
from fuzzer import ParameterFuzzer
from payloads import get_payloads_by_type
from rate_limiter import build_stealth_options
from reporting import (
    compare_scans,
    generate_csv_export,
    generate_html_report,
    generate_json_report,
    generate_markdown_report,
    generate_statistics,
)
from templates import get_all_templates, get_template, template_to_sqlmap_options
from waf_bypass import WAFBypassEngine

api = Blueprint("api_extended", __name__, url_prefix="/api")


# Statistics & Dashboard
@api.route("/statistics", methods=["GET"])
def get_statistics():
    stats = generate_statistics()
    return jsonify(stats)


# Vulnerability Management
@api.route("/vulnerabilities", methods=["GET"])
def get_vulnerabilities():
    severity = request.args.get("severity")
    status = request.args.get("status")
    limit = int(request.args.get("limit", 100))

    vulns = VulnerabilityDB.get_all(severity, status, limit)
    return jsonify({"vulnerabilities": vulns, "total": len(vulns)})


@api.route("/vulnerabilities/<int:vuln_id>", methods=["PATCH"])
def update_vulnerability(vuln_id):
    data = request.json or {}
    status = data.get("status")
    notes = data.get("remediation_notes")
    is_fp = data.get("false_positive")

    if status:
        VulnerabilityDB.update_status(vuln_id, status, notes)
    if is_fp is not None:
        VulnerabilityDB.mark_false_positive(vuln_id, is_fp)

    return jsonify({"message": "Updated"})


# Scan Templates
@api.route("/templates", methods=["GET"])
def list_templates():
    templates = get_all_templates()
    return jsonify({"templates": templates})


@api.route("/templates/<template_id>", methods=["GET"])
def get_template_details(template_id):
    template = get_template(template_id)
    if not template:
        return jsonify({"error": "Template not found"}), 404
    return jsonify(template)


@api.route("/templates/<template_id>/options", methods=["GET"])
def get_template_options(template_id):
    template = get_template(template_id)
    if not template:
        return jsonify({"error": "Template not found"}), 404

    options = template_to_sqlmap_options(template)
    return jsonify({"options": options, "options_string": " ".join(options)})


# Custom Payloads
@api.route("/payloads", methods=["GET"])
def list_payloads():
    payload_type = request.args.get("type")
    database_type = request.args.get("database")

    payloads = PayloadDB.get_all(payload_type, database_type)
    return jsonify({"payloads": payloads})


@api.route("/payloads", methods=["POST"])
def create_payload():
    data = request.json or {}

    payload_id = PayloadDB.create(
        name=data["name"],
        payload_type=data["type"],
        payload=data["payload"],
        database_type=data.get("database_type"),
        description=data.get("description"),
        tags=data.get("tags"),
    )

    return jsonify({"id": payload_id, "message": "Payload created"})


# Parameter Fuzzing
@api.route("/fuzz/generate", methods=["POST"])
def generate_fuzz_payloads():
    data = request.json or {}
    fuzz_types = data.get("types", ["all"])

    payload_set = ParameterFuzzer.generate_fuzzing_payload_set(fuzz_types)

    return jsonify(
        {"payload_set": payload_set, "total": sum(len(p) for p in payload_set.values())}
    )


@api.route("/fuzz/parameter", methods=["POST"])
def fuzz_parameter():
    data = request.json or {}
    base_url = data.get("url")
    parameter = data.get("parameter")
    fuzz_types = data.get("types")

    if not base_url or not parameter:
        return jsonify({"error": "URL and parameter required"}), 400

    fuzzed_urls = ParameterFuzzer.fuzz_parameter(base_url, parameter, fuzz_types)

    return jsonify({"fuzzed_urls": fuzzed_urls, "total": len(fuzzed_urls)})


# Scan Queue
@api.route("/queue", methods=["GET"])
def get_queue():
    status = request.args.get("status")
    queue_items = QueueDB.get_all(status)
    return jsonify({"queue": queue_items})


@api.route("/queue", methods=["POST"])
def add_to_queue():
    data = request.json or {}
    scan_id = data.get("scan_id")
    priority = data.get("priority", 0)
    scheduled_time = data.get("scheduled_time")
    max_retries = data.get("max_retries", 0)

    if not scan_id:
        return jsonify({"error": "scan_id required"}), 400

    queue_id = QueueDB.add(scan_id, priority, scheduled_time, max_retries)
    return jsonify({"queue_id": queue_id, "message": "Added to queue"})


# Reporting
@api.route("/reports/<scan_id>/html", methods=["GET"])
def get_html_report(scan_id):
    html = generate_html_report(scan_id)
    return Response(html, mimetype="text/html")


@api.route("/reports/<scan_id>/markdown", methods=["GET"])
def get_markdown_report(scan_id):
    md = generate_markdown_report(scan_id)
    return Response(md, mimetype="text/markdown")


@api.route("/reports/<scan_id>/json", methods=["GET"])
def get_json_report(scan_id):
    json_report = generate_json_report(scan_id)
    return Response(json_report, mimetype="application/json")


@api.route("/reports/csv", methods=["POST"])
def export_csv():
    data = request.json or {}
    scan_ids = data.get("scan_ids", [])

    scans = [ScanDB.get(sid) for sid in scan_ids if ScanDB.get(sid)]
    csv_content = generate_csv_export(scans)

    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=scans.csv"},
    )


@api.route("/reports/compare", methods=["POST"])
def compare_scan_reports():
    data = request.json or {}
    scan_id1 = data.get("scan_id1")
    scan_id2 = data.get("scan_id2")

    if not scan_id1 or not scan_id2:
        return jsonify({"error": "Both scan IDs required"}), 400

    comparison = compare_scans(scan_id1, scan_id2)
    return jsonify(comparison)


# Custom Scripts
@api.route("/scripts", methods=["GET"])
def list_scripts():
    script_type = request.args.get("type")
    if script_type:
        scripts = ScriptDB.get_enabled(script_type)
    else:
        scripts = []
    return jsonify({"scripts": scripts})


@api.route("/scripts", methods=["POST"])
def create_script():
    data = request.json or {}

    script_id = ScriptDB.create(
        script_id=str(uuid.uuid4()),
        name=data["name"],
        script_type=data["type"],
        code=data["code"],
        enabled=data.get("enabled", True),
    )

    return jsonify({"id": script_id, "message": "Script created"})


# Error Logs
@api.route("/errors", methods=["GET"])
def get_error_logs():
    limit = int(request.args.get("limit", 50))
    errors = ErrorLogDB.get_recent(limit)
    return jsonify({"errors": errors})


# Stealth Mode
@api.route("/stealth/options", methods=["POST"])
def get_stealth_options():
    data = request.json or {}

    rate_limit = data.get("rate_limit")
    user_agent_rotation = data.get("user_agent_rotation", False)
    random_delays = data.get("random_delays", False)
    proxy = data.get("proxy")

    options = build_stealth_options(
        rate_limit=rate_limit,
        user_agent_rotation=user_agent_rotation,
        random_delays=random_delays,
        proxy=proxy,
    )

    return jsonify({"options": options, "options_string": " ".join(options)})


# Advanced Search
@api.route("/search", methods=["GET"])
def advanced_search():
    query = request.args.get("q", "")
    limit = int(request.args.get("limit", 50))

    if not query:
        return jsonify({"results": []})

    results = ScanDB.search(query, limit)
    return jsonify({"results": results, "total": len(results)})


# Session Management Helper
@api.route("/session/cookies", methods=["POST"])
def manage_session_cookies():
    data = request.json or {}
    cookies = data.get("cookies", {})

    cookie_string = "; ".join([f"{k}={v}" for k, v in cookies.items()])

    return jsonify(
        {"cookie_string": cookie_string, "sqlmap_option": f'--cookie="{cookie_string}"'}
    )


@api.route("/session/headers", methods=["POST"])
def manage_session_headers():
    data = request.json or {}
    headers = data.get("headers", {})

    header_options = []
    for key, value in headers.items():
        header_options.extend(["--header", f"{key}: {value}"])

    return jsonify(
        {"header_options": header_options, "options_string": " ".join(header_options)}
    )


# AI-Powered Analysis
@api.route("/ai/analyze-injection", methods=["POST"])
def analyze_injection():
    data = request.json or {}
    response_text = data.get("response", "")
    payload = data.get("payload", "")

    analysis = VulnerabilityAnalyzer.analyze_injection_type(response_text, payload)
    return jsonify(analysis)


@api.route("/ai/calculate-severity", methods=["POST"])
def calculate_severity():
    data = request.json or {}
    vuln_type = data.get("type")
    impact = data.get("impact", "medium")
    exploitability = data.get("exploitability", "medium")
    context = data.get("context", {})

    severity, score, justification = VulnerabilityAnalyzer.calculate_severity(
        vuln_type, impact, exploitability, context
    )

    return jsonify(
        {"severity": severity, "score": score, "justification": justification}
    )


@api.route("/ai/remediation", methods=["POST"])
def get_remediation():
    data = request.json or {}
    vuln_type = data.get("type")
    context = data.get("context", {})

    remediation = VulnerabilityAnalyzer.generate_remediation(vuln_type, context)
    return jsonify(remediation)


@api.route("/ai/detect-waf", methods=["POST"])
def detect_waf():
    data = request.json or {}
    headers = data.get("headers", {})
    body = data.get("body", "")

    waf_info = VulnerabilityAnalyzer.detect_waf(headers, body)
    return jsonify(waf_info)


@api.route("/ai/exploitation-chain", methods=["POST"])
def analyze_exploitation_chain():
    data = request.json or {}
    vulnerabilities = data.get("vulnerabilities", [])

    chains = VulnerabilityAnalyzer.analyze_exploitation_chain(vulnerabilities)
    return jsonify(chains)


@api.route("/ai/predict-next-steps", methods=["POST"])
def predict_next_steps():
    data = request.json or {}
    current_findings = data.get("findings", [])

    suggestions = VulnerabilityAnalyzer.predict_next_steps(current_findings)
    return jsonify({"suggestions": suggestions, "total": len(suggestions)})


# WAF Bypass Engine
@api.route("/waf/generate-bypasses", methods=["POST"])
def generate_waf_bypasses():
    data = request.json or {}
    base_payload = data.get("payload")
    count = data.get("count", 10)

    if not base_payload:
        return jsonify({"error": "Payload required"}), 400

    payloads = WAFBypassEngine.generate_tampered_payloads(base_payload, count)
    return jsonify({"payloads": payloads, "total": len(payloads)})


@api.route("/waf/adaptive-bypass", methods=["POST"])
def adaptive_waf_bypass():
    data = request.json or {}
    waf_type = data.get("waf_type")
    base_payload = data.get("payload")
    blocked_techniques = data.get("blocked_techniques", [])

    if not waf_type or not base_payload:
        return jsonify({"error": "WAF type and payload required"}), 400

    result = WAFBypassEngine.adaptive_bypass(waf_type, base_payload, blocked_techniques)
    return jsonify(result)


@api.route("/waf/test-effectiveness", methods=["POST"])
def test_waf_effectiveness():
    data = request.json or {}
    payload = data.get("payload")
    response_code = data.get("response_code")
    response_body = data.get("response_body", "")

    if not payload or response_code is None:
        return jsonify({"error": "Payload and response_code required"}), 400

    result = WAFBypassEngine.test_payload_effectiveness(
        payload, response_code, response_body
    )
    return jsonify(result)


@api.route("/waf/rate-limit-evasion", methods=["GET"])
def get_rate_limit_evasion():
    strategies = WAFBypassEngine.generate_rate_limit_evasion()
    return jsonify(strategies)


# Health Check with Feature Status
@api.route("/health/features", methods=["GET"])
def feature_health():
    return jsonify(
        {
            "status": "healthy",
            "features": {
                "authentication": "enabled",
                "ai_analysis": "enabled",
                "waf_bypass": "enabled",
                "websockets": "enabled",
                "queue_processor": "enabled",
                "vulnerability_tracking": "enabled",
                "templates": "enabled",
                "fuzzing": "enabled",
                "reporting": "enabled",
            },
            "version": "2.1.0-advanced",
        }
    )


def register_extended_routes(app):
    """Register all extended API routes"""
    app.register_blueprint(api)
