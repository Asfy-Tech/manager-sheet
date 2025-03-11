import time
import threading
from datetime import datetime
from pathlib import Path
from config.settings import settings
import json
from app.models.watch_path import WatchPathDB
from app.models.task import TaskDB
from app.models.notification import NotificationDB
from app.services.google_sheets import GoogleSheets 
class FileWatcher:
    def __init__(self, interval=60):
        self.interval = interval
        self._running = False
        self._last_check = {}
        self.task_db = TaskDB()
        self.notification_db = NotificationDB()
        self.watch_path_db = WatchPathDB()
        self._thread = None  # Chỉ lưu 1 thread duy nhất

    def _get_file_info(self, path: Path) -> dict:
        stats = path.stat()
        return {
            'name': path.name,
            'path': str(path),
            'size': stats.st_size,
            'modified_time': datetime.fromtimestamp(stats.st_mtime),
            'status': 'Modified'
        }
    
    def _check_task_status(self, task_id: str, new_status: str) -> bool:
        """
        Check if task needs sheet update
        Returns: True if sheet update needed, False otherwise
        """
        db_task = self.task_db.get_task(task_id)
        completed_status = settings.TASK_STATUS_SUCCESS

        # Case 1: New task with completed status
        if not db_task and new_status == completed_status:
            return True # Need update and send

        # Case 2: Existing task with status changes involving completed status
        if db_task:
            db_status = db_task.get('status')
            # Task changed from complete to incomplete
            if db_status == completed_status and new_status != completed_status:
                return True # Need update and send
            # Task changed from incomplete to complete
            if db_status != completed_status and new_status == completed_status:
                return True # Need update and send

        return False

    def _process_sheet_tasks(self, company: dict, data: list, headers: list):
        """Process tasks from a sheet"""
        tasks_to_upsert = []
        gg_sheets = GoogleSheets()
        sheet_updates_needed = []

        for row in data:
            row_upper = {k.upper(): v for k, v in row.items()}
            task_id = row_upper.get(settings.TASK_ID)
            status = row_upper.get(settings.TASK_STATUS, "")

            if not task_id:  # Skip rows without task ID
                continue

            if self._check_task_status(task_id, status):
                sheet_updates_needed.append({
                    'task_id': task_id,
                    'status': status
                })

            tasks_to_upsert.append({
                'task_id': task_id,
                'status': status
            })

        # Bulk upsert tasks
        if tasks_to_upsert:
            success = self.task_db.bulk_upsert_tasks(tasks_to_upsert)
            if not success:
                print(f"❌ Error upserting tasks for {company.get('name')}")

        # Print sheet update notifications
        if sheet_updates_needed:
            print(f"\n🔄 Sheet updates needed for {company.get('name')}:")
            for task in sheet_updates_needed:
                gg_sheets.update_task(task['task_id'],task['status'])

    def _check_files(self):
        """Giả lập kiểm tra file"""
        gg_sheets = GoogleSheets()
        companies = self.watch_path_db.get_all_paths()
        for company in companies:
            try:
                link = company.get('link')
                res = gg_sheets.get_data_from_link(link, 'Tasks')
                if res is None:
                    print(f"❌ Cannot access sheet for {company.get('name')}")
                    self.watch_path_db.update_path_status(company.get('id'), 'deactive')
                    continue

                self.watch_path_db.update_path_status(company.get('id'), 'active')
                headers = res.get('headers')
                data = res.get('data')
                lower_headers = [h.upper() for h in headers]
                if settings.TASK_ID not in lower_headers or settings.TASK_STATUS not in lower_headers:
                    print(f"❌ Invalid sheet format for {company.get('name')}")
                    self.watch_path_db.update_path_status(company.get('id'), 'deactive')
                    continue
                
                print(f"\n📊 Processing {company.get('name')}...")
                self._process_sheet_tasks(company, data, headers)

            except Exception as e:
                self.notification_db.add_notification(
                    title=f"Công ty: {company.get('name')}",
                    content=f"Không thể đọc dược dữ liệu!"
                )
                print(f"Lỗi khi đọc công ty: {company.get('name')}",e)

    def start(self):
        """Bắt đầu quá trình theo dõi file"""
        if self._running:
            print("FileWatcher đã chạy rồi, không khởi động lại.")
            return

        self._running = True

        def run():
            while self._running:
                
                print("=> Start")
                self._check_files()

                for i in range(self.interval, 0, -1):
                    print(f"Chờ: {i}s")
                    time.sleep(1)

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()

    def stop(self):
        """Dừng quá trình theo dõi file"""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join()
            print("FileWatcher đã dừng.")
