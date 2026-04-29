"""
WebSocket manager for real-time scan output streaming
"""

import logging
import queue
import threading
from typing import Dict, Set

from flask_socketio import SocketIO, emit, join_room, leave_room

logger = logging.getLogger(__name__)

socketio = None
_scan_rooms: Dict[str, Set[str]] = {}
_room_lock = threading.Lock()


def init_socketio(app):
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")
    setup_handlers()
    return socketio


def setup_handlers():
    @socketio.on("connect")
    def handle_connect():
        logger.info(f"Client connected: {request.sid}")
        emit("connected", {"status": "connected"})

    @socketio.on("disconnect")
    def handle_disconnect():
        logger.info(f"Client disconnected: {request.sid}")
        with _room_lock:
            for scan_id, clients in list(_scan_rooms.items()):
                if request.sid in clients:
                    clients.remove(request.sid)
                    if not clients:
                        del _scan_rooms[scan_id]

    @socketio.on("join_scan")
    def handle_join_scan(data):
        scan_id = data.get("scan_id")
        if scan_id:
            join_room(scan_id)
            with _room_lock:
                if scan_id not in _scan_rooms:
                    _scan_rooms[scan_id] = set()
                _scan_rooms[scan_id].add(request.sid)
            logger.info(f"Client {request.sid} joined scan room: {scan_id}")
            emit("joined_scan", {"scan_id": scan_id})

    @socketio.on("leave_scan")
    def handle_leave_scan(data):
        scan_id = data.get("scan_id")
        if scan_id:
            leave_room(scan_id)
            with _room_lock:
                if scan_id in _scan_rooms and request.sid in _scan_rooms[scan_id]:
                    _scan_rooms[scan_id].remove(request.sid)
                    if not _scan_rooms[scan_id]:
                        del _scan_rooms[scan_id]
            logger.info(f"Client {request.sid} left scan room: {scan_id}")
            emit("left_scan", {"scan_id": scan_id})


def emit_scan_output(scan_id: str, output: str, output_type: str = "stdout"):
    """Emit scan output to all clients watching this scan"""
    if socketio:
        socketio.emit(
            "scan_output",
            {"scan_id": scan_id, "output": output, "type": output_type},
            room=scan_id,
        )


def emit_scan_status(
    scan_id: str, status: str, progress: int = None, details: str = None
):
    """Emit scan status update"""
    if socketio:
        data = {"scan_id": scan_id, "status": status}
        if progress is not None:
            data["progress"] = progress
        if details:
            data["details"] = details
        socketio.emit("scan_status", data, room=scan_id)


def emit_scan_complete(
    scan_id: str, success: bool, exit_code: int = None, vulnerabilities: int = 0
):
    """Emit scan completion"""
    if socketio:
        socketio.emit(
            "scan_complete",
            {
                "scan_id": scan_id,
                "success": success,
                "exit_code": exit_code,
                "vulnerabilities": vulnerabilities,
            },
            room=scan_id,
        )


def emit_vulnerability_found(scan_id: str, vulnerability: Dict):
    """Emit vulnerability discovery in real-time"""
    if socketio:
        socketio.emit(
            "vulnerability_found",
            {"scan_id": scan_id, "vulnerability": vulnerability},
            room=scan_id,
        )


def emit_error(scan_id: str, error: str, error_type: str = "error"):
    """Emit error message"""
    if socketio:
        socketio.emit(
            "scan_error",
            {"scan_id": scan_id, "error": error, "error_type": error_type},
            room=scan_id,
        )


from flask import request
