import time
import threading
from datetime import datetime
from pathlib import Path
from config.settings import settings
import os
import json
from app.models.companies import Companies
from app.models.tasks import Task
from app.models.notifications import Notification
import pytz
from app.services.google_sheets import GoogleSheets 
vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
class FileWatcher:
    def __init__(self, interval=60):
        self.interval = interval
        self._running = False
        self._last_check = {}
        self._thread = None
        self._cache = {}
        self.init_cache()

    def init_cache(self):
        """Đọc nội dung từ file cache/tasks.json và xử lý lỗi"""
        try:
            if os.path.exists('cache/tasks.json'):
                with open('cache/tasks.json', 'r', encoding='utf-8') as f:
                    try:
                        self._cache = json.load(f) 
                    except json.JSONDecodeError:
                        print("Lỗi định dạng JSON trong file 'cache/tasks.json'")
            else:
                print("File 'cache/tasks.json' không tồn tại.")
        except Exception as e:
            print(f"Đã xảy ra lỗi khi đọc file: {e}")

    def _get_file_info(self, path: Path) -> dict:
        stats = path.stat()
        return {
            'name': path.name,
            'path': str(path),
            'size': stats.st_size,
            'modified_time': datetime.fromtimestamp(stats.st_mtime),
            'status': 'Modified'
        }
    
    def _check_task_status(self, sheet: dict, sheet_cache: dict):
        current_status = sheet.get(settings.TASK_STATUS)

        current_time_vn = datetime.now(vn_timezone)
        formatted_time = current_time_vn.strftime("%H:%M %d/%m/%Y")

        completed_status = settings.TASK_STATUS_SUCCESS

        # Case 1: New task with completed status
        if sheet_cache is None:
            if current_status == completed_status:
                return True, formatted_time
            else:
                return True, ''
            
        old_status = sheet_cache.get(settings.TASK_STATUS)

        # Case 2: Existing task with status changes involving completed status
        # Task changed from incomplete to complete
        if old_status != completed_status and current_status == completed_status:
            return True, formatted_time
        
        # Task changed from complete to incomplete
        if old_status == completed_status and current_status != completed_status:
            return True, ''

        return False, None

    def _process_sheet_tasks(self, data_sheets):
        gg_sheets = GoogleSheets()
        data_cache = self._cache
        self._cache = data_sheets
        if not os.path.exists('cache'):
            os.makedirs('cache')
        with open('cache/tasks.json', 'w', encoding='utf-8') as f:
            json.dump(data_sheets, f, indent=4, ensure_ascii=False)
        
        sheet_updates_needed = {}

        for sheet_id, sheet in data_sheets.items():
            sheet_cache = data_cache.get(sheet_id)
            checkUpdate, time = self._check_task_status(sheet, sheet_cache)
            if checkUpdate and time is not None:
                print(f"{sheet_id} - {time}")
                sheet[settings.TASK_FINISH_DATE] = time
            sheet_updates_needed[sheet_id] = sheet
        # print(json.dumps(sheet_updates_needed, indent=4, ensure_ascii=False))
        # return
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
                    if dt.get(settings.TASK_ID):
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
