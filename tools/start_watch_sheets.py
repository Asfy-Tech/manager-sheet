import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config.settings import settings
from app.monitors.file_watcher import FileWatcher
watcher = FileWatcher(interval=settings.SYNC_INTERVAL)
watcher.start()