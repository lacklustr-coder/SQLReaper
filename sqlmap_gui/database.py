"""
Database models and schema for SQLReaper
"""

import json
import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

DB_PATH = os.path.join(os.path.dirname(__file__), "results", "sqlreaper.db")
_local = threading.local()


def get_connection():
    if not hasattr(_local, "conn"):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        _local.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _local.conn.row_factory = sqlite3.Row
    return _local.conn


@contextmanager
def get_cursor():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()


def init_database():
    with get_cursor() as cursor:
        # Scans table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id TEXT PRIMARY KEY,
                target TEXT NOT NULL,
                scan_type TEXT NOT NULL,
                options TEXT,
                status TEXT NOT NULL,
                exit_code INTEGER,
                output TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_seconds INTEGER,
                bookmarked INTEGER DEFAULT 0,
                tags TEXT,
                project_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Vulnerabilities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id TEXT NOT NULL,
                vuln_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                parameter TEXT,
                payload TEXT,
                database_type TEXT,
                description TEXT,
                evidence TEXT,
                status TEXT DEFAULT 'new',
                remediation_notes TEXT,
                false_positive INTEGER DEFAULT 0,
                cve_id TEXT,
                owasp_category TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE CASCADE
            )
        """)

        # Projects table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                client_name TEXT,
                scope TEXT,
                status TEXT DEFAULT 'active',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Scan queue table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scan_queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id TEXT UNIQUE NOT NULL,
                priority INTEGER DEFAULT 0,
                scheduled_time TEXT,
                status TEXT DEFAULT 'pending',
                retry_count INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)

        # Payloads table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                payload_type TEXT NOT NULL,
                database_type TEXT,
                payload TEXT NOT NULL,
                description TEXT,
                tags TEXT,
                success_rate REAL DEFAULT 0.0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Scan templates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scan_templates (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                template_type TEXT NOT NULL,
                options TEXT NOT NULL,
                is_default INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Custom scripts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_scripts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                script_type TEXT NOT NULL,
                code TEXT NOT NULL,
                enabled INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Error logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id TEXT,
                error_type TEXT NOT NULL,
                error_message TEXT NOT NULL,
                stack_trace TEXT,
                retry_attempted INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (scan_id) REFERENCES scans(id) ON DELETE SET NULL
            )
        """)

        # Settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scans_target ON scans(target)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_scans_status ON scans(status)")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_scans_created ON scans(created_at)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_vulns_scan ON vulnerabilities(scan_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_vulns_severity ON vulnerabilities(severity)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_vulns_status ON vulnerabilities(status)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_queue_status ON scan_queue(status)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_queue_priority ON scan_queue(priority DESC)"
        )


def row_to_dict(row) -> Dict[str, Any]:
    if row is None:
        return None
    return dict(zip(row.keys(), row))


class ScanDB:
    @staticmethod
    def create(
        scan_id: str,
        target: str,
        scan_type: str,
        options: str = None,
        project_id: str = None,
        tags: List[str] = None,
    ) -> str:
        now = datetime.now().isoformat()
        with get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO scans (id, target, scan_type, options, status, start_time,
                                   created_at, updated_at, project_id, tags)
                VALUES (?, ?, ?, ?, 'pending', ?, ?, ?, ?)
            """,
                (
                    scan_id,
                    target,
                    scan_type,
                    options,
                    now,
                    now,
                    now,
                    json.dumps(tags) if tags else None,
                    project_id,
                ),
            )
        return scan_id

    @staticmethod
    def update_status(
        scan_id: str,
        status: str,
        exit_code: int = None,
        output: str = None,
        end_time: str = None,
    ):
        now = datetime.now().isoformat()
        with get_cursor() as cursor:
            cursor.execute(
                """
                UPDATE scans SET status = ?, exit_code = ?, output = ?,
                                end_time = ?, updated_at = ?
                WHERE id = ?
            """,
                (status, exit_code, output, end_time or now, now, scan_id),
            )

    @staticmethod
    def get(scan_id: str) -> Optional[Dict]:
        with get_cursor() as cursor:
            cursor.execute("SELECT * FROM scans WHERE id = ?", (scan_id,))
            return row_to_dict(cursor.fetchone())

    @staticmethod
    def get_all(
        limit: int = 100,
        offset: int = 0,
        status: str = None,
        project_id: str = None,
        tags: List[str] = None,
    ) -> List[Dict]:
        with get_cursor() as cursor:
            query = "SELECT * FROM scans WHERE 1=1"
            params = []

            if status:
                query += " AND status = ?"
                params.append(status)
            if project_id:
                query += " AND project_id = ?"
                params.append(project_id)
            if tags:
                for tag in tags:
                    query += " AND tags LIKE ?"
                    params.append(f'%"{tag}"%')

            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            return [row_to_dict(row) for row in cursor.fetchall()]

    @staticmethod
    def search(query: str, limit: int = 50) -> List[Dict]:
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM scans
                WHERE target LIKE ? OR output LIKE ? OR tags LIKE ?
                ORDER BY created_at DESC LIMIT ?
            """,
                (f"%{query}%", f"%{query}%", f"%{query}%", limit),
            )
            return [row_to_dict(row) for row in cursor.fetchall()]

    @staticmethod
    def delete(scan_id: str):
        with get_cursor() as cursor:
            cursor.execute("DELETE FROM scans WHERE id = ?", (scan_id,))


class VulnerabilityDB:
    @staticmethod
    def create(
        scan_id: str,
        vuln_type: str,
        severity: str,
        parameter: str = None,
        payload: str = None,
        database_type: str = None,
        description: str = None,
        evidence: str = None,
        owasp_category: str = None,
    ) -> int:
        now = datetime.now().isoformat()
        with get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO vulnerabilities
                (scan_id, vuln_type, severity, parameter, payload, database_type,
                 description, evidence, owasp_category, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    scan_id,
                    vuln_type,
                    severity,
                    parameter,
                    payload,
                    database_type,
                    description,
                    evidence,
                    owasp_category,
                    now,
                    now,
                ),
            )
            return cursor.lastrowid

    @staticmethod
    def update_status(vuln_id: int, status: str, remediation_notes: str = None):
        now = datetime.now().isoformat()
        with get_cursor() as cursor:
            cursor.execute(
                """
                UPDATE vulnerabilities
                SET status = ?, remediation_notes = ?, updated_at = ?
                WHERE id = ?
            """,
                (status, remediation_notes, now, vuln_id),
            )

    @staticmethod
    def mark_false_positive(vuln_id: int, is_fp: bool = True):
        now = datetime.now().isoformat()
        with get_cursor() as cursor:
            cursor.execute(
                """
                UPDATE vulnerabilities SET false_positive = ?, updated_at = ?
                WHERE id = ?
            """,
                (1 if is_fp else 0, now, vuln_id),
            )

    @staticmethod
    def get_by_scan(scan_id: str) -> List[Dict]:
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM vulnerabilities WHERE scan_id = ?
                ORDER BY
                    CASE severity
                        WHEN 'critical' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                        ELSE 5
                    END, created_at DESC
            """,
                (scan_id,),
            )
            return [row_to_dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_all(
        severity: str = None, status: str = None, limit: int = 100
    ) -> List[Dict]:
        with get_cursor() as cursor:
            query = "SELECT * FROM vulnerabilities WHERE 1=1"
            params = []

            if severity:
                query += " AND severity = ?"
                params.append(severity)
            if status:
                query += " AND status = ?"
                params.append(status)

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            return [row_to_dict(row) for row in cursor.fetchall()]

    @staticmethod
    def deduplicate(target: str, vuln_type: str, parameter: str) -> Optional[Dict]:
        """Find existing vulnerability with same target/type/parameter"""
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT v.* FROM vulnerabilities v
                JOIN scans s ON v.scan_id = s.id
                WHERE s.target = ? AND v.vuln_type = ? AND v.parameter = ?
                AND v.false_positive = 0
                ORDER BY v.created_at DESC LIMIT 1
            """,
                (target, vuln_type, parameter),
            )
            return row_to_dict(cursor.fetchone())


class PayloadDB:
    @staticmethod
    def create(
        name: str,
        payload_type: str,
        payload: str,
        database_type: str = None,
        description: str = None,
        tags: List[str] = None,
    ) -> int:
        now = datetime.now().isoformat()
        with get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO payloads
                (name, payload_type, payload, database_type, description, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    name,
                    payload_type,
                    payload,
                    database_type,
                    description,
                    json.dumps(tags) if tags else None,
                    now,
                    now,
                ),
            )
            return cursor.lastrowid

    @staticmethod
    def get_all(payload_type: str = None, database_type: str = None) -> List[Dict]:
        with get_cursor() as cursor:
            query = "SELECT * FROM payloads WHERE 1=1"
            params = []

            if payload_type:
                query += " AND payload_type = ?"
                params.append(payload_type)
            if database_type:
                query += " AND (database_type = ? OR database_type IS NULL)"
                params.append(database_type)

            query += " ORDER BY success_rate DESC, name"
            cursor.execute(query, params)
            return [row_to_dict(row) for row in cursor.fetchall()]

    @staticmethod
    def update_success_rate(payload_id: int, success_rate: float):
        now = datetime.now().isoformat()
        with get_cursor() as cursor:
            cursor.execute(
                """
                UPDATE payloads SET success_rate = ?, updated_at = ?
                WHERE id = ?
            """,
                (success_rate, now, payload_id),
            )


class TemplateDB:
    @staticmethod
    def create(
        template_id: str,
        name: str,
        template_type: str,
        options: Dict,
        description: str = None,
        is_default: bool = False,
    ) -> str:
        now = datetime.now().isoformat()
        with get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO scan_templates
                (id, name, description, template_type, options, is_default, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    template_id,
                    name,
                    description,
                    template_type,
                    json.dumps(options),
                    1 if is_default else 0,
                    now,
                    now,
                ),
            )
        return template_id

    @staticmethod
    def get_all() -> List[Dict]:
        with get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM scan_templates ORDER BY is_default DESC, name"
            )
            rows = [row_to_dict(row) for row in cursor.fetchall()]
            for row in rows:
                if row and row.get("options"):
                    row["options"] = json.loads(row["options"])
            return rows

    @staticmethod
    def get(template_id: str) -> Optional[Dict]:
        with get_cursor() as cursor:
            cursor.execute("SELECT * FROM scan_templates WHERE id = ?", (template_id,))
            row = row_to_dict(cursor.fetchone())
            if row and row.get("options"):
                row["options"] = json.loads(row["options"])
            return row


class ScriptDB:
    @staticmethod
    def create(
        script_id: str, name: str, script_type: str, code: str, enabled: bool = True
    ) -> str:
        now = datetime.now().isoformat()
        with get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO custom_scripts
                (id, name, script_type, code, enabled, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (script_id, name, script_type, code, 1 if enabled else 0, now, now),
            )
        return script_id

    @staticmethod
    def get_enabled(script_type: str) -> List[Dict]:
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM custom_scripts
                WHERE script_type = ? AND enabled = 1
                ORDER BY name
            """,
                (script_type,),
            )
            return [row_to_dict(row) for row in cursor.fetchall()]


class ErrorLogDB:
    @staticmethod
    def create(
        error_type: str,
        error_message: str,
        scan_id: str = None,
        stack_trace: str = None,
    ) -> int:
        now = datetime.now().isoformat()
        with get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO error_logs
                (scan_id, error_type, error_message, stack_trace, created_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (scan_id, error_type, error_message, stack_trace, now),
            )
            return cursor.lastrowid

    @staticmethod
    def get_recent(limit: int = 50) -> List[Dict]:
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM error_logs ORDER BY created_at DESC LIMIT ?
            """,
                (limit,),
            )
            return [row_to_dict(row) for row in cursor.fetchall()]


class QueueDB:
    @staticmethod
    def add(
        scan_id: str,
        priority: int = 0,
        scheduled_time: str = None,
        max_retries: int = 0,
    ) -> int:
        now = datetime.now().isoformat()
        with get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO scan_queue
                (scan_id, priority, scheduled_time, max_retries, created_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (scan_id, priority, scheduled_time, max_retries, now),
            )
            return cursor.lastrowid

    @staticmethod
    def get_next() -> Optional[Dict]:
        with get_cursor() as cursor:
            cursor.execute(
                """
                SELECT * FROM scan_queue
                WHERE status = 'pending'
                AND (scheduled_time IS NULL OR scheduled_time <= ?)
                ORDER BY priority DESC, created_at ASC LIMIT 1
            """,
                (datetime.now().isoformat(),),
            )
            return row_to_dict(cursor.fetchone())

    @staticmethod
    def update_status(queue_id: int, status: str, retry_count: int = None):
        with get_cursor() as cursor:
            if retry_count is not None:
                cursor.execute(
                    """
                    UPDATE scan_queue SET status = ?, retry_count = ?
                    WHERE id = ?
                """,
                    (status, retry_count, queue_id),
                )
            else:
                cursor.execute(
                    """
                    UPDATE scan_queue SET status = ? WHERE id = ?
                """,
                    (status, queue_id),
                )

    @staticmethod
    def get_all(status: str = None) -> List[Dict]:
        with get_cursor() as cursor:
            if status:
                cursor.execute(
                    """
                    SELECT * FROM scan_queue WHERE status = ?
                    ORDER BY priority DESC, created_at
                """,
                    (status,),
                )
            else:
                cursor.execute("""
                    SELECT * FROM scan_queue ORDER BY priority DESC, created_at
                """)
            return [row_to_dict(row) for row in cursor.fetchall()]
