import sqlite3
from config.settings import settings

class TaskDB:
    def __init__(self):
        self.db_path = settings.DATABASE_PATH
        self._init_db()
    
    def _init_db(self):
        """Initialize tasks table"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(f'''
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    status TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def add_task(self, task_id: str, status: str = None) -> bool:
        """Add new task"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    f"INSERT INTO tasks (task_id, status) VALUES (?, ?)",
                    (task_id, status)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False

    def update_task_status(self, task_id: str, status: str) -> bool:
        """Update task status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    f"""
                    UPDATE tasks 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE task_id = ?
                    """,
                    (status, task_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception:
            return False

    def get_task(self, task_id: str) -> dict:
        """Get task by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                f"""
                SELECT task_id, status, created_at, updated_at
                FROM tasks
                WHERE task_id = ?
                """,
                (task_id,)
            )
            result = cursor.fetchone()
            return dict(result) if result else None

    def get_all_tasks(self) -> list:
        """Get all tasks"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                f"""
                SELECT task_id, status, created_at, updated_at
                FROM tasks
                ORDER BY updated_at DESC
                """
            )
            return [dict(row) for row in cursor.fetchall()]

    def bulk_upsert_tasks(self, tasks: list) -> bool:
        """
        Bulk upsert tasks
        Args:
            tasks: List of dicts with task_id and status
        Returns:
            bool: Success status
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                for task in tasks:
                    conn.execute(
                        f"""
                        INSERT INTO tasks (task_id, status)
                        VALUES (?, ?)
                        ON CONFLICT(task_id) DO UPDATE SET
                            status = excluded.status,
                            updated_at = CURRENT_TIMESTAMP
                        """,
                        (task['task_id'], task['status'])
                    )
                conn.commit()
                return True
        except Exception as e:
            print(f"Error in bulk upsert: {str(e)}")
            return False