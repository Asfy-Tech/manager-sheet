import time
import threading
from datetime import datetime
from pathlib import Path
from config.settings import settings
from flask import session
import json
from app.models.companies import Companies
from app.models.tasks import Task
from app.models.notifications import Notification
from app.services.google_sheets import GoogleSheets 
class FileWatcher:
    def __init__(self, interval=60):
        self.interval = interval
        self._running = False
        self._last_check = {}
        self._thread = None
        self._cache = {}

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
        db_task = Task.get_task(task_id)
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

    def _process_sheet_tasks(self, data_sheets):
        gg_sheets = GoogleSheets()
        data_cache = self._cache
        self._cache = data_sheets
        
        sheet_updates_needed = {}

        for sheet_id, sheet in data_sheets.items():
            sheet_updates_needed[sheet_id] = sheet

        success = gg_sheets.update_task(sheet_updates_needed)
        print(f'Status Import: {success}')

    def _check_files(self):
        """Giả lập kiểm tra file"""
        gg_sheets = GoogleSheets()
        companies = Companies.get()
        data_sheets = {}
        for company in companies:
            try:
                link = company.sheet_link
                res = gg_sheets.get_data_from_link(link, 'Tasks')
                if res is None:
                    print(f"❌ Cannot access sheet for {company.name}")
                    company.update(status='deactive')
                    raise Exception('Không thể đọc dữ liệu!')

                company.update(status='active')
                headers = res.get('headers')
                data = res.get('data')
                lower_headers = [h.upper() for h in headers]
                if settings.TASK_ID not in lower_headers or settings.TASK_STATUS not in lower_headers:
                    print(f"❌ Invalid sheet format for {company.name}")
                    company.update(status='deactive')
                    raise Exception(f'Cột: {settings.TASK_ID} hoặc {settings.TASK_STATUS} không tồn tại!')
                
                print(f"\n📊 Processing {company.name}...")
                for dt in data:
                    data_sheets[dt.get(settings.TASK_ID)] = dt

            except Exception as e:
                Notification.create(
                    title=f"Công ty: {company.name}",
                    content=e
                )
                print(f"Lỗi khi đọc công ty: {company.name}",e)
        self._process_sheet_tasks(data_sheets)

    def start(self):
        """Bắt đầu quá trình theo dõi file"""
        if self._running:
            print("FileWatcher đã chạy rồi, không khởi động lại.")
            return

        self._running = True
        def run():
            index = 0
            while self._running:
                index += 1
                print(f"=> Start: {index}")
                self._check_files()
                if index >= 2: 
                    break 
                for i in range(self.interval, 0, -1):
                    print(f"Chờ: {i}s")
                    time.sleep(1)
        run()
        # self._thread = threading.Thread(target=run, daemon=True)
        # self._thread.start()

    def stop(self):
        """Dừng quá trình theo dõi file"""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join()
            print("FileWatcher đã dừng.")
