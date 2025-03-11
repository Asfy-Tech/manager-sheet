from app.monitors.file_watcher import FileWatcher
watcher = FileWatcher(interval=30)
watcher._check_files()

# from app.models.base import Base, engine

# Base.metadata.create_all(engine)