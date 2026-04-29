"""
Scan queue processor for managing concurrent scans
"""

import logging
import threading
import time
from typing import Optional

from database import QueueDB, ScanDB
from scan_executor import execute_scan

logger = logging.getLogger(__name__)


class QueueProcessor:
    def __init__(self, max_concurrent: int = 3):
        self.max_concurrent = max_concurrent
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.active_scans = set()
        self.lock = threading.Lock()

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._process_loop, daemon=True)
        self.thread.start()
        logger.info(f"Queue processor started (max_concurrent={self.max_concurrent})")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Queue processor stopped")

    def _process_loop(self):
        while self.running:
            try:
                with self.lock:
                    active_count = len(self.active_scans)

                if active_count < self.max_concurrent:
                    queue_item = QueueDB.get_next()
                    if queue_item:
                        self._start_queued_scan(queue_item)

                time.sleep(2)
            except Exception as e:
                logger.error(f"Queue processor error: {e}", exc_info=True)
                time.sleep(5)

    def _start_queued_scan(self, queue_item: dict):
        scan_id = queue_item["scan_id"]
        queue_id = queue_item["id"]

        with self.lock:
            if scan_id in self.active_scans:
                return
            self.active_scans.add(scan_id)

        QueueDB.update_status(queue_id, "running")

        def scan_callback(success: bool):
            with self.lock:
                self.active_scans.discard(scan_id)

            if success:
                QueueDB.update_status(queue_id, "completed")
            else:
                retry_count = queue_item["retry_count"] + 1
                max_retries = queue_item["max_retries"]

                if max_retries > 0 and retry_count < max_retries:
                    QueueDB.update_status(queue_id, "pending", retry_count)
                    logger.info(
                        f"Scan {scan_id} failed, retrying ({retry_count}/{max_retries})"
                    )
                else:
                    QueueDB.update_status(queue_id, "failed")
                    logger.error(f"Scan {scan_id} failed permanently")

        scan_data = ScanDB.get(scan_id)
        if scan_data:
            threading.Thread(
                target=lambda: execute_scan(scan_data, callback=scan_callback),
                daemon=True,
            ).start()


queue_processor = QueueProcessor()
