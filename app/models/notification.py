import sqlite3
from datetime import datetime
from config.settings import settings
import pytz

class NotificationDB:
    def __init__(self):
        self.db_path = settings.DATABASE_PATH
        self._init_db()
    
    def _init_db(self):
        """Initialize notifications table"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def add_notification(self, title: str, content: str) -> bool:
        """Add new notification"""
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        now_vn = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(vn_tz)
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO notifications (title, content, created_at) VALUES (?, ?, ?)",
                    (title, content, now_vn.strftime('%Y-%m-%d %H:%M:%S'))
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding notification: {e}")
            return False

    def get_notifications(self, limit: int = 50, offset: int = 0) -> list:
        """Get notifications with pagination"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT id, title, content, created_at 
                FROM notifications 
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (limit, offset))
            return [dict(row) for row in cursor.fetchall()]

    def delete_old_notifications(self, days: int = 30) -> bool:
        """Delete notifications older than specified days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    DELETE FROM notifications 
                    WHERE datetime(created_at) < datetime('now', ?)
                ''', (f'-{days} days',))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error deleting old notifications: {e}")
            return False