import time
import random
import gc
from datetime import datetime, timedelta
from pathlib import Path
from config.settings import settings
import os
import json
from app.services.bot_telegram import BotFather
from app.models.companies import Companies
from app.models.notifications import Notification
import pytz
from app.models.telegram_message import TelegramMessage
from app.services.google_sheets import GoogleSheets 
vn_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
class FileWatcher:
    def __init__(self, interval=60):
        self.interval = interval
        self._running = False
        self._last_check = {}
        self._thread = None
        self._cache = {}
        self._cache_city = []
        self._messages = {
            'late': [],
            'today': [],
            'future': [],
        }
        self.init_cache()

    def init_cache(self):
        """Đọc nội dung từ file cache/tasks.json và xử lý lỗi"""
        file_path = 'cache/tasks.json'
        # Đảm bảo thư mục cache tồn tại
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        self._cache = json.load(f)
                    except json.JSONDecodeError:
                        # print("Error format json file, create new file...")
                        self.create_default_cache(file_path)
            else:
                # print("File not exit, create new file...")
                self.create_default_cache(file_path)
        except Exception as e:
            # print(f"Error when read file: {e}")
            self.create_default_cache(file_path)

    def create_default_cache(self, file_path):
        """Tạo file cache/tasks.json với nội dung mặc định là {}"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=4, ensure_ascii=False)
            # print("Create file 'cache/tasks.json' success!")
        except Exception as e:
            print(f"Error when create file: {e}")

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
            self._check_and_send_message(sheet_id, sheet)
            checkUpdate, time = self._check_task_status(sheet, sheet_cache)
            if checkUpdate and time is not None:
                sheet[settings.TASK_FINISH_DATE] = time
            sheet_updates_needed[sheet_id] = sheet
        list_created = gg_sheets.update_task(sheet_updates_needed)
        bot = BotFather()
        bot.send_multiple_tasks(self._messages)
        bot.send_multiple_task_created_at(list_created)

    def _check_and_send_message(self, sheet_id, sheet):
        deadline_str = sheet.get(settings.TASK_DEADLINE)
        status_str = sheet.get(settings.TASK_STATUS)
        if not deadline_str or not status_str:
            return
        
        if status_str == settings.TASK_STATUS_SUCCESS:
            return
        
        try:
            deadline = datetime.strptime(deadline_str, "%d/%m/%Y").date()
        except ValueError:
            # print(f"Error date format - {deadline_str}")
            return

        current_time = datetime.now(vn_timezone)
        current_date_vn = current_time.date()

        one_day_later = current_date_vn + timedelta(days=1)
        two_days_later = current_date_vn + timedelta(days=2)

        if deadline > two_days_later:
            return

        data = {
            "category": sheet.get("HẠNG MỤC"),
            "todo": sheet.get("VIỆC CẦN LÀM"),
            "representative": sheet.get("PHỤ TRÁCH"),
            "company": sheet.get("CÔNG TY"),
            "support": sheet.get("HỖ TRỢ"),
            "status": sheet.get("TRẠNG THÁI"),
            "deadline": deadline,
            "delay": (current_date_vn - deadline).days if deadline else None,
        }
    
        if deadline == one_day_later:
            data['type'] = 3
        elif deadline == current_date_vn:
            data['type'] = 2
        else:
            data['type'] = 1

        task = TelegramMessage.find_by_task_and_date(sheet_id, current_date_vn)
        if task:
            pass
            # if current_time.hour < 8:
            #     task.update(**data)
        else:
            task = TelegramMessage.create(task_id=sheet_id, **data)

        if current_time.hour >= 8 and task.is_seen == False:
            row = {
                'task': task,
                'sheet': sheet,
            }
            if deadline == one_day_later:
                self._messages['future'].append(row)
            elif deadline == current_date_vn:
                self._messages['today'].append(row)
            else:
                self._messages['late'].append(row)

    def _check_files(self, gg_sheets):
        """Giả lập kiểm tra file"""
        # print('Open google sheets')
        companies = Companies.get_sorted_by_last_active()
        data_sheets = {}
        self._messages = {'late': [], 'today': [], 'future': []}
        generate_task_id = {}
        for company in companies:
            try:
                # print(f'Start company: {company.id}')
                link = company.sheet_link
                res = gg_sheets.get_data_from_link(link, 'Tasks', formatJson=True)
                # print(f'Read success company: {company.id}')
                if res is None:
                    company.update(status='deactive')
                    raise Exception('Không thể đọc dữ liệu!')
                company.update(status='active')
                # print(f'-> Get data success company: {company.id}')
                headers = res.get('headers')
                data = res.get('data')
                lower_headers = [h.upper() for h in headers]
                if settings.TASK_ID not in lower_headers or settings.TASK_STATUS not in lower_headers:
                    company.update(status='deactive')
                    raise Exception(f'Cột: {settings.TASK_ID} hoặc {settings.TASK_STATUS} không tồn tại!')
                
                # print(f'-><- Yes data success company: {company.id}')
                for dt in data:
                    if not dt.get(settings.TASK_ID):
                        if any(value for key, value in dt.items() if key != "row_id"):
                            dt[settings.TASK_ID] = f"TASK_{int(time.time() * 1000)}{random.randint(100, 999)}"
                            if company.id not in generate_task_id:
                                generate_task_id[company.id] = {
                                    "data": res,
                                    "name": company.name,
                                    "link": link,
                                    'main_sheet_id': company.main_sheet_id,
                                    "updates": []
                                }
                            generate_task_id[company.id]["updates"].append({
                                'row_id': dt.get('row_id'),
                                'value': dt[settings.TASK_ID],
                            })
                            # print(f"Generated task_id: {dt[settings.TASK_ID]} for company: {company.name}")

                    if dt.get(settings.TASK_ID):
                        dt['CÔNG TY'] = company.name
                        data_sheets[dt.get(settings.TASK_ID)] = dt
                 
                company.update(last_active=datetime.now(vn_timezone))
                if company.id in self._cache_city:
                    self._cache_city.remove(company.id)
            except Exception as e:
                # print(f"Error read company: {company.name}: {e}")
                if company.id not in self._cache_city:
                    self._cache_city.append(company.id)
                    Notification.create(
                        title=f"Công ty: {company.name}",
                        content=e
                    )
        # print('Read full file success')
        if generate_task_id:
            gg_sheets.update_task_ids(generate_task_id)
        self._process_sheet_tasks(data_sheets)
        data_sheets.clear()
        generate_task_id.clear()
        del data_sheets
        gc.collect()

    def start(self):
        # print('Start google sheet')
        gg_sheets = GoogleSheets()
        # print('Done')
        while True:
            try:
                self._check_files(gg_sheets)
            except Exception as e:
                print(f'Error read file: {e}')
            for i in range(180, 0, -1):
                time.sleep(1)

    def stop(self):
        """Dừng quá trình theo dõi file"""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join()
            print("FileWatcher stoped.")
