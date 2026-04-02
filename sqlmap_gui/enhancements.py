"""
SQLMap GUI - Enhancements Module
System Tray, Auto-Save, and helper utilities
"""
import threading
import json
import os
import logging
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)
RESULTS_DIR = 'results'

class AutoSave:
    """Auto-save scan results when scans complete"""
    def __init__(self, save_dir: str = None):
        self.save_dir = save_dir or RESULTS_DIR
        os.makedirs(self.save_dir, exist_ok=True)
        self._file = os.path.join(self.save_dir, 'autosave.json')
        self._data: List[Dict] = self._load()

    def _load(self) -> List[Dict]:
        if os.path.exists(self._file):
            with open(self._file, 'r') as f:
                return json.load(f)
        return []

    def _save(self):
        with open(self._file, 'w') as f:
            json.dump(self._data, f, indent=2)

    def save(self, scan_id: str, target: str, output: str, status: str, code: int = 0):
        entry = {
            'id': scan_id, 'target': target,
            'output': output, 'status': status,
            'code': code, 'ts': datetime.now().isoformat()
        }
        self._data.append(entry)
        self._data = self._data[-100:]
        self._save()
        logger.info(f"Auto-saved scan: {scan_id} ({status})")

    def get_all(self) -> List[Dict]:
        return list(self._data)

autosave = AutoSave()


class TrayManager:
    """Simple system tray manager"""
    def __init__(self):
        self.icon = None
        self._callbacks: Dict[str, Callable] = {}
        self._thread: Optional[threading.Thread] = None

    def register(self, name: str, fn: Callable):
        self._callbacks[name] = fn

    def start(self):
        try:
            import pystray
            from PIL import Image, ImageDraw
            img = self._make_icon()
            menu = pystray.Menu(
                pystray.MenuItem('Show', self._cb_show, default=True),
                pystray.MenuItem('Scan', self._cb_scan),
                pystray.MenuItem('Stop', self._cb_stop),
                pystray.MenuItem('Exit', self._cb_exit),
            )
            self.icon = pystray.Icon('sqlmap', img, 'SQLMap', menu)
            self._thread = threading.Thread(target=self.icon.run, daemon=True)
            self._thread.start()
            logger.info("Tray started")
        except Exception as e:
            logger.warning(f"Tray failed: {e}")

    def _make_icon(self):
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
            d = ImageDraw.Draw(img)
            d.ellipse([4, 4, 60, 60], fill=(0, 180, 0, 220))
            d.ellipse([0, 0, 64, 64], outline=(0, 255, 68, 100), width=2)
            return img
        except:
            from PIL import Image
            return Image.new('RGBA', (64, 64), (0, 180, 0, 200))

    def _cb_show(self, icon=None, item=None):
        if 'show' in self._callbacks:
            self._callbacks['show']()
    def _cb_scan(self, icon=None, item=None):
        if 'scan' in self._callbacks:
            self._callbacks['scan']()
    def _cb_stop(self, icon=None, item=None):
        if 'stop' in self._callbacks:
            self._callbacks['stop']()
    def _cb_exit(self, icon=None, item=None):
        if 'exit' in self._callbacks:
            self._callbacks['exit']()
        if self.icon:
            self.icon.stop()

    def set_status(self, txt: str):
        if self.icon:
            self.icon.title = f"SQLMap: {txt}"

    def stop(self):
        if self.icon:
            try:
                self.icon.stop()
            except:
                pass

tray = TrayManager()