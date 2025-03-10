import sqlite3
from datetime import datetime
from config.settings import settings

class WatchPathDB:
    def __init__(self):
        self.db_path = settings.DATABASE_PATH
        self._init_db()

    def get_path_by_id(self, id: int) -> dict:
        """Get watch path by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT id, name, link, created_at FROM watch_paths WHERE id = ?", 
                (id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def _init_db(self):
        """Initialize database with new schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS watch_paths (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    link TEXT NOT NULL UNIQUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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

    def add_path(self, name: str, link: str) -> bool:
        """Add new watch path"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO watch_paths (name, link) VALUES (?, ?)",
                    (name, link)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
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

    def get_all_paths(self) -> list:
        """Get all watch paths"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT id, name, link, created_at 
                FROM watch_paths 
                ORDER BY created_at DESC
            ''')
            return [dict(row) for row in cursor.fetchall()]

    def log_change(self, file_info: dict):
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