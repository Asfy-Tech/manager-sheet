from app.monitors.file_watcher import FileWatcher
watcher = FileWatcher(interval=30)
watcher._check_files()
