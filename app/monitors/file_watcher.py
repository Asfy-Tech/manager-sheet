import time
import threading
from datetime import datetime
from pathlib import Path
from app.models.watch_path import WatchPathDB
from config.settings import settings

class FileWatcher:
    def __init__(self, interval=60):
        self.interval = interval
        self._running = False
        self._last_check = {}
        self.watch_path_db = WatchPathDB()

    def _get_file_info(self, path: Path) -> dict:
        stats = path.stat()
        return {
            'name': path.name,
            'path': str(path),
            'size': stats.st_size,
            'modified_time': datetime.fromtimestamp(stats.st_mtime),
            'status': 'Modified'
        }

    def _check_files(self):
        paths = self.watch_path_db.get_all_paths()
        
        for _, path, _, _ in paths:
            try:
                path = Path(path)
                if not path.exists():
                    continue

                current_mtime = path.stat().st_mtime
                if path not in self._last_check or self._last_check[path] != current_mtime:
                    self._last_check[path] = current_mtime
                    file_info = self._get_file_info(path)
                    self.watch_path_db.log_change(file_info)
                    
            except Exception as e:
                print(f"Error checking {path}: {e}")

    def start(self):
        if self._running:
            return

        self._running = True
        def run():
            while self._running:
                self._check_files()
                time.sleep(self.interval)

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if hasattr(self, '_thread'):
            self._thread.join()