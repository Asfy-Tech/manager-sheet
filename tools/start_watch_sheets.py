import sys
import os
print("Helo moi nguoi")
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config.settings import settings
from app.monitors.file_watcher import FileWatcher
watcher = FileWatcher(interval=settings.SYNC_INTERVAL)
print("Start Interval")
watcher.start()