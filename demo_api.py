#!/usr/bin/env python3
"""
SQLReaper v2.1 Advanced - API Demo Script
Demonstrates the new AI-powered and WAF bypass features
"""

import json
from typing import Any, Dict

import requests

# Configuration
BASE_URL = "http://localhost:5000"
USERNAME = "admin"
PASSWORD = "admin123"


class SQLReaperClient:
    """Client for SQLReaper API"""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}

    def login(self, username: str, password: str) -> bool:
        """Authenticate and get JWT token"""
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"username": username, "password": password},
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data["token"]
            self.headers["Authorization"] = f"Bearer {self.token}"
            print(
                f"✓ Authenticated as {data['user']['username']} ({data['user']['role']})"
            )
            return True
        else:
            print(f"✗ Login failed: {response.json()}")
            return False

    def analyze_injection(self, response_text: str, payload: str) -> Dict:
        """Use AI to analyze injection type"""
        response = requests.post(
            f"{self.base_url}/api/ai/analyze-injection",
            json={"response": response_text, "payload": payload},
            headers=self.headers,
        )
        return response.json()

    def calculate_severity(
        self,
        vuln_type: str,
        impact: str = "high",
        exploitability: str = "easy",
        context: Dict = None,
    ) -> Dict:
        """Calculate vulnerability severity"""
        response = requests.post(
            f"{self.base_url}/api/ai/calculate-severity",
            json={
                "type": vuln_type,
                "impact": impact,
                "exploitability": exploitability,
                "context": context or {},
            },
            headers=self.headers,
        )
        return response.json()

    def get_remediation(self, vuln_type: str, context: Dict = None) -> Dict:
        """Get automated remediation suggestions"""
        response = requests.post(
            f"{self.base_url}/api/ai/remediation",
            json={"type": vuln_type, "context": context or {}},
            headers=self.headers,
        )
        return response.json()

    def detect_waf(self, headers: Dict, body: str) -> Dict:
        """Detect Web Application Firewall"""
        response = requests.post(
            f"{self.base_url}/api/ai/detect-waf",
            json={"headers": headers, "body": body},
            headers=self.headers,
        )
        return response.json()

    def analyze_exploitation_chain(self, vulnerabilities: list) -> Dict:
        """Analyze vulnerability chaining opportunities"""
        response = requests.post(
            f"{self.base_url}/api/ai/exploitation-chain",
            json={"vulnerabilities": vulnerabilities},
            headers=self.headers,
        )
        return response.json()

    def predict_next_steps(self, findings: list) -> Dict:
        """Get AI-powered next step suggestions"""
        response = requests.post(
            f"{self.base_url}/api/ai/predict-next-steps",
            json={"findings": findings},
            headers=self.headers,
        )
        return response.json()

    def generate_waf_bypasses(self, payload: str, count: int = 10) -> Dict:
        """Generate WAF bypass payload variations"""
        response = requests.post(
            f"{self.base_url}/api/waf/generate-bypasses",
            json={"payload": payload, "count": count},
            headers=self.headers,
        )
        return response.json()

    def adaptive_waf_bypass(
        self, waf_type: str, payload: str, blocked_techniques: list = None
    ) -> Dict:
        """Generate WAF-specific bypass payloads"""
        response = requests.post(
            f"{self.base_url}/api/waf/adaptive-bypass",
            json={
                "waf_type": waf_type,
                "payload": payload,
                "blocked_techniques": blocked_techniques or [],
            },
            headers=self.headers,
        )
        return response.json()

    def get_feature_health(self) -> Dict:
        """Check feature availability"""
        response = requests.get(f"{self.base_url}/api/health/features")
        return response.json()


def print_section(title: str):
    """Print a section header"""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def demo_ai_analysis(client: SQLReaperClient):
    """Demo AI-powered analysis features"""
    print_section("AI-Powered Vulnerability Analysis")

    # Demo 1: Injection Type Detection
    print("1. Analyzing SQL Injection Type...")
    analysis = client.analyze_injection(
        response_text="mysql_fetch_array() expects parameter 1 to be resource, boolean given in /var/www/html/users.php on line 23",
        payload="' OR '1'='1",
    )
    print(f"   Injection Types: {', '.join(analysis['injection_types'])}")
    print(f"   Confidence: {analysis['confidence']}%")
    print(f"   Analysis: {analysis['analysis'][:100]}...")

    # Demo 2: Severity Calculation
    print("\n2. Calculating Severity Score...")
    severity = client.calculate_severity(
        vuln_type="sqli",
        impact="high",
        exploitability="easy",
        context={"public_facing": True, "authenticated": False, "data_sensitive": True},
    )
    print(f"   Severity: {severity['severity']}")
    print(f"   Score: {severity['score']}/10.0")
    print(f"   Justification: {severity['justification'][:100]}...")

    # Demo 3: Remediation Suggestions
    print("\n3. Generating Remediation Plan...")
    remediation = client.get_remediation(
        vuln_type="sqli", context={"framework": "Flask"}
    )
    print(f"   Immediate Actions: {len(remediation['immediate'])} steps")
    print(f"   - {remediation['immediate'][0]}")
    print(f"   Short-term Actions: {len(remediation['short_term'])} steps")
    print(f"   - {remediation['short_term'][0]}")


def demo_waf_detection(client: SQLReaperClient):
    """Demo WAF detection"""
    print_section("WAF Detection & Analysis")

    print("Detecting WAF from response...")
    waf_info = client.detect_waf(
        headers={"server": "cloudflare", "cf-ray": "123abc"},
        body="Attention Required! | Cloudflare",
    )
    print(f"   WAF Detected: {waf_info['detected']}")
    if waf_info["detected"]:
        print(f"   WAF Type(s): {', '.join(waf_info['wafs'])}")
        print(
            f"   Bypass Suggestions: {len(waf_info['bypass_suggestions'])} techniques"
        )
        for i, suggestion in enumerate(waf_info["bypass_suggestions"][:3], 1):
            print(f"     {i}. {suggestion}")


def demo_exploitation_chains(client: SQLReaperClient):
    """Demo exploitation chain analysis"""
    print_section("Exploitation Chain Analysis")

    print("Analyzing vulnerability chaining opportunities...")
    chains = client.analyze_exploitation_chain(
        vulnerabilities=[
            {"type": "sqli", "severity": "high", "url": "/admin.php"},
            {"type": "lfi", "severity": "medium", "url": "/download.php"},
        ]
    )
    print(f"   Chains Found: {chains['chains_found']}")
    if chains["chains_found"] > 0:
        chain = chains["chains"][0]
        print(f"\n   Chain: {chain['name']}")
        print(f"   Impact: {chain['impact']}")
        print(f"   Description: {chain['description']}")
        print(f"   Steps:")
        for i, step in enumerate(chain["steps"], 1):
            print(f"     {i}. {step}")


def demo_next_steps(client: SQLReaperClient):
    """Demo AI-powered next step prediction"""
    print_section("AI-Powered Next Step Prediction")

    print("Predicting next penetration testing steps...")
    suggestions = client.predict_next_steps(
        findings=[{"type": "sqli", "url": "/products.php?id=1", "severity": "high"}]
    )
    print(f"   Suggestions: {suggestions['total']} actions recommended\n")
    for i, suggestion in enumerate(suggestions["suggestions"][:5], 1):
        print(f"   {i}. {suggestion['action']} [{suggestion['priority']}]")
        print(f"      Reason: {suggestion['reason']}")
        print(f"      Command: {suggestion['command']}\n")


def demo_waf_bypass(client: SQLReaperClient):
    """Demo WAF bypass engine"""
    print_section("Advanced WAF Bypass Engine")

    # Demo 1: Generate bypass variations
    print("1. Generating WAF Bypass Variations...")
    base_payload = "' UNION SELECT 1,2,3--"
    bypasses = client.generate_waf_bypasses(payload=base_payload, count=5)
    print(f"   Generated {bypasses['total']} bypass variations:\n")
    for i, bypass in enumerate(bypasses["payloads"][:3], 1):
        print(f"   {i}. Technique: {bypass['technique']}")
        print(f"      Payload: {bypass['payload'][:80]}...")
        print()

    # Demo 2: WAF-specific adaptive bypass
    print("2. Cloudflare-Specific Adaptive Bypass...")
    adaptive = client.adaptive_waf_bypass(
        waf_type="Cloudflare", payload=base_payload, blocked_techniques=["Case Mix"]
    )
    print(f"   WAF Type: {adaptive['waf_type']}")
    print(f"   Generated {adaptive['total_variations']} variations")
    print(f"   Recommended Strategies:")
    for i, strategy in enumerate(adaptive["recommended_strategies"][:3], 1):
        print(f"     {i}. {strategy}")


def demo_feature_health(client: SQLReaperClient):
    """Demo feature health check"""
    print_section("Feature Health Check")

    health = client.get_feature_health()
    print(f"Status: {health['status']}")
    print(f"Version: {health['version']}\n")
    print("Features:")
    for feature, status in health["features"].items():
        emoji = "✓" if status == "enabled" else "✗"
        print(f"  {emoji} {feature}: {status}")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("  SQLReaper v2.1 Advanced - API Demo")
    print("=" * 70)

    client = SQLReaperClient(BASE_URL)

    # Check health first (no auth required)
    try:
        demo_feature_health(client)
    except Exception as e:
        print(f"✗ Server not reachable: {e}")
        print(f"\nMake sure SQLReaper is running at {BASE_URL}")
        return

    # Login
    print_section("Authentication")
    if not client.login(USERNAME, PASSWORD):
        print("Authentication failed. Demo cannot continue.")
        return

    # Run demos
    try:
        demo_ai_analysis(client)
        demo_waf_detection(client)
        demo_exploitation_chains(client)
        demo_next_steps(client)
        demo_waf_bypass(client)

        print_section("Demo Complete!")
        print("All advanced features demonstrated successfully!")
        print("\nFor more information, see:")
        print("  - FEATURES.md - Complete feature documentation")
        print("  - AIKIDO_SETUP.md - Security scanning setup")
        print("  - README.md - General usage")

    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
