from config.settings import settings
from app.monitors.file_watcher import FileWatcher
watcher = FileWatcher(interval=settings.SYNC_INTERVAL)
print("Start Interval")
watcher.start()