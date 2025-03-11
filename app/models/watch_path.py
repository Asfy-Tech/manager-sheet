import sqlite3
from datetime import datetime
from config.settings import settings
import pytz

class WatchPathDB:
    def __init__(self):
        self.db_path = settings.DATABASE_PATH
        self._init_db()

    def _init_db(self):
        """Initialize database with updated schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS watch_paths (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    link TEXT NOT NULL UNIQUE,
                    status TEXT DEFAULT 'active',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

            conn.execute('''
                CREATE TABLE IF NOT EXISTS file_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    size INTEGER,
                    modified_time DATETIME,
                    status TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def add_path(self, name: str, link: str, status="active") -> bool:
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now_vn = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(vn_tz)
        """Add new watch path"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO watch_paths (name, link, status, updated_at) VALUES (?, ?, ?, ?)",
                    (name, link, status, now_vn.strftime('%Y-%m-%d %H:%M:%S'))
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def get_path_by_id(self, id: int) -> dict:
        """Get watch path by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT id, name, link, status, created_at, updated_at FROM watch_paths WHERE id = ?", 
                (id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_all_paths(self) -> list:
        """Get all watch paths"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT id, name, link, status, created_at, updated_at 
                FROM watch_paths 
                ORDER BY created_at DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]

    def update_path_status(self, id: int, status: str) -> bool:
        """Update the status of a watch path"""
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now_vn = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(vn_tz)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "UPDATE watch_paths SET status = ?, updated_at = ? WHERE id = ?",
                    (status, now_vn.strftime('%Y-%m-%d %H:%M:%S'), id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False

    def delete_path(self, id: int) -> bool:
        """Delete a watch path by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("DELETE FROM watch_paths WHERE id = ?", (id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False

    def log_change(self, file_info: dict):
        """Log file changes"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO file_changes 
                (file_name, file_path, size, modified_time, status)
                VALUES (?, ?, ?, ?, ?)
            """, (
                file_info['name'],
                file_info['path'],
                file_info['size'],
                file_info['modified_time'],
                file_info['status']
            ))
