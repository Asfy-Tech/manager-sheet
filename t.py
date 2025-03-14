
# # from app.monitors.file_watcher import FileWatcher
# # watcher = FileWatcher(interval=30)
# # watcher._check_files()

# # from app.models.base import Base, engine
# from app.models.telegram_message import TelegramMessage
# # from app.models.telegram_users import TelegramUser
# # from app.models.users import User
# # from app.models.companies import Companies
# # from app.models.notifications import Notification
# # from app.models.tasks import Task
# # Base.metadata.create_all(engine)
# # from config import hash_password
# # from datetime import datetime

# # User.create(
# #     name="Phạm Văn Hùng",
# #     email="supperment",
# #     password=hash_password("hungpv"),
# #     role="admin",
# #     status=True,
# #     avatar="https://example.com/avatar.jpg",
# #     last_login=datetime.utcnow()
# # )
# # # admins = TelegramUser.get(role=1)
# # # print(len(admins))

from googleapiclient.discovery import build
from google.oauth2 import service_account
import json
def dd(data):
    """In ra dữ liệu dưới dạng JSON đẹp"""
    print(json.dumps(data, indent=4, ensure_ascii=False))

# Cấu hình Google API
SERVICE_ACCOUNT_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

def get_sheet_values(spreadsheet_id, sheet_name):
    """Lấy dữ liệu từ Google Sheets, bao gồm cả đường link nếu có."""
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("sheets", "v4", credentials=creds)

    # Lấy dữ liệu có cả hyperlink
    sheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id, ranges=sheet_name, includeGridData=True).execute()

    values = []
    for row in sheet["sheets"][0]["data"][0]["rowData"]:
        row_values = []
        for cell in row.get("values", []):
            if "hyperlink" in cell:
                # Nếu ô có hyperlink, bọc trong thẻ <a>
                link = cell["hyperlink"]
                text = cell.get("formattedValue", link)
                row_values.append(f"<a href='{link}' target='_blank'>{text}</a>")
            else:
                # Nếu không có link, trả về giá trị bình thường
                row_values.append(cell.get("formattedValue", ""))
        values.append(row_values)

    return values

# Thông tin Google Sheet
spreadsheet_id = "1ChRpSsLIC6QVhl87I4Jlb7sz-DldvAShE-BdHq29uEU"
sheet_name = "Tasks"

# Gọi hàm để lấy dữ liệu
values = get_sheet_values(spreadsheet_id, sheet_name)

filtered_data = [row for row in values if any(cell.strip() for cell in row)]

for row in filtered_data:
    dd(row)
