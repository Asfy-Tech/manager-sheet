import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from config.settings import settings
import re
from app.models.notifications import Notification
from googleapiclient.errors import HttpError
from datetime import datetime
import json

class GoogleSheets:
    def __init__(self):
        self.credentials = service_account.Credentials.from_service_account_file(
            settings.CREDENTIALS_PATH,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        self.service = build('sheets', 'v4', credentials=self.credentials)
        self.sheet = self.service.spreadsheets()
    

    def getIndexCol(self, headers, col):
        task_id_col = None
        for idx, header in enumerate(headers):
            if header.upper() == col:
                task_id_col = idx
        return task_id_col
    
    def update_task(self, sheet_data, sheet_name='Tasks'):
        list_created = []
        """
        Cập nhật trạng thái task trong Google Sheet.
        Args:
            sheet_data: Dữ liệu cần cập nhật
            sheet_name: Tên sheet (mặc định: 'Tasks')
        Returns:
            bool: True nếu thành công, False nếu thất bại.
        """
        is_valid, main_sheet_id  = self.set_id_from_path_sheet(settings.GOOGLE_SHEET_MAIN_LINK)
        if not is_valid:
            return list_created


        # Lấy dữ liệu hiện có trong Google Sheets
        result = self.sheet.values().get(spreadsheetId=main_sheet_id, range=sheet_name).execute()
        values = result.get('values', [])
        if not values:
            # print("No find data to sheet")
            return list_created

        headers = values[0] if values else []
        task_id_col = self.getIndexCol(headers, settings.TASK_ID)
        if task_id_col is None:
            # print(f"No find col {settings.TASK_ID}")
            return list_created

        existing_task_ids = set()
        updates = []

        create_row = 1
        rows_without_task_id = []
        for idx, row in enumerate(values[1:], start=1):
            if len(row) <= task_id_col or not row[task_id_col].strip():
                rows_without_task_id.append(idx+1) 


        # Duyệt qua danh sách cần cập nhật
        for sheet_id, sheet in sheet_data.items():
            try:
                existing_task_ids.add(sheet_id)
                row_idx = None

                # Tìm hàng có task ID tương ứng
                for idx, row in enumerate(values[1:], start=1):
                    if len(row) > task_id_col and row[task_id_col] == sheet_id:
                        row_idx = idx
                        break


                if row_idx is None:
                    # print(f"➡ Task ID {sheet_id} not found, create new")
                    list_created.append(sheet)
                    row_idx = len(values)
                    new_row = [''] * len(headers)
                    new_row[task_id_col] = sheet_id
                    for col, value in sheet.items():
                        col_idx = self.getIndexCol(headers, col)
                        if col_idx is not None:
                            if isinstance(value, dict) and "link" in value and "text" in value:
                                new_row[col_idx] = f'=HYPERLINK("{value["link"]}", "{value["text"]}")'
                            else:
                                new_row[col_idx] = value
                    updates.append({'range': f"{sheet_name}!A{row_idx + create_row}", 'values': [new_row]})
                    create_row += 1
                    continue

                # Cập nhật dữ liệu nếu task đã tồn tại
                for col, value in sheet.items():
                    if col == settings.TASK_ID:
                        continue
                    col_idx = self.getIndexCol(headers, col)
                    if col_idx is not None:
                        if isinstance(value, dict) and "link" in value and "text" in value:
                            updates.append({'range': f"{sheet_name}!{chr(65 + col_idx)}{row_idx + 1}", 'values': [[f'=HYPERLINK("{value["link"]}"; "{value["text"]}")']]})
                        else:
                            updates.append({'range': f"{sheet_name}!{chr(65 + col_idx)}{row_idx + 1}", 'values': [[value]]})
            except Exception as e:
                print(f"Error when update task {sheet_id}: {e}")
                continue

        # Gửi batch update
        if updates:
            # print('😉 Chưa gặp lỗi:')
            self.sheet.values().batchUpdate(spreadsheetId=main_sheet_id, body={'valueInputOption': 'USER_ENTERED', 'data': updates}).execute()
            # print('😒 Đã gặp lỗi:')

        # Xóa các task không còn tồn tại
        # if len(existing_task_ids) > 0:
        self.delete_tasks(values, existing_task_ids, main_sheet_id, rows_without_task_id)
        return list_created


    def delete_tasks(self, values, existing_task_ids,main_sheet_id, rows_without_task_id):
        # print(rows_without_task_id)
        """
        Xóa các task không còn tồn tại trong danh sách cập nhật.
        """
        headers = values[0] if values else []
        task_id_col = self.getIndexCol(headers, settings.TASK_ID)
        if task_id_col is None:
            # print(f"No find column {settings.TASK_ID}")
            return False

        # Danh sách task ID hiện tại
        current_existing_task_ids = {row[task_id_col] for row in values[1:] if len(row) > task_id_col}

        # Danh sách cần xóa
        tasks_to_delete = current_existing_task_ids - set(existing_task_ids)

        # if not tasks_to_delete:
        #     print("No task need delete")
        #     return True

        rows_to_delete = [
            idx for idx, row in enumerate(values[1:], start=2)
            if len(row) > task_id_col and row[task_id_col] in tasks_to_delete
        ]

        rows_to_delete.extend(rows_without_task_id)

        if not rows_to_delete:
            # print("No delete")
            return True

        # Xóa từ hàng cuối để tránh lệch index
        rows_to_delete.sort(reverse=True)

        # Gửi batch request để xóa hàng
        requests = [{
            "deleteDimension": {
                "range": {
                    "sheetId": int(settings.MAIN_SHEET_ID),  # Sử dụng đúng sheetId thay vì mặc định 0
                    "dimension": "ROWS",
                    "startIndex": idx - 1,
                    "endIndex": idx
                }
            }
        } for idx in rows_to_delete]

        self.service.spreadsheets().batchUpdate(spreadsheetId=main_sheet_id, body={"requests": requests}).execute()

        # print("Deleted success")
        return True

    def set_id_from_path_sheet(self, url):
        pattern = r'/d/([a-zA-Z0-9-_]+)'
        match = re.search(pattern, url)
        
        if not match:
            return False, None
        
        sheet_id = match.group(1)
        return True, sheet_id


    def validate_sheet_url(self, url: str) -> tuple:
        """
        Validate Google Sheet URL and check if it's accessible
        Returns: (is_valid: bool, sheet_id: str, error_message: str)
        """
        # Extract sheet ID from URL using regex
        pattern = r'/d/([a-zA-Z0-9-_]+)'
        match = re.search(pattern, url)
        
        if not match:
            return False, None, "Invalid Google Sheet URL format", {}
        
        sheet_id = match.group(1)
        
        try:
            # Try to get sheet metadata
            sheet = self.service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            sheets = sheet.get('sheets', [])
            sheet_ids = {s['properties']['title']: s['properties']['sheetId'] for s in sheets}
            return True, sheet_id, "Sheet is accessible", sheet_ids
        except HttpError as e:
            if e.resp.status == 403:
                return False, sheet_id, "Permission denied. Make sure the sheet is shared with the service account", {}
            elif e.resp.status == 404:
                return False, sheet_id, "Sheet not found", {}
            else:
                return False, sheet_id, f"Error accessing sheet: {str(e)}", {}
        except Exception as e:
            return False, sheet_id, f"Unexpected error: {str(e)}", {}
        
    def get_sheet_names(self, url: str):
        """
        Lấy danh sách các sheet (worksheet) từ một Google Spreadsheet
        """
        # Trích xuất Sheet ID từ URL
        pattern = r'/d/([a-zA-Z0-9-_]+)'
        match = re.search(pattern, url)

        if not match:
            return {"error": "Invalid Google Sheet URL format"}

        sheet_id = match.group(1)

        try:
            # Lấy thông tin về các sheet trong spreadsheet
            response = self.sheet.get(spreadsheetId=sheet_id).execute()
            sheets = response.get("sheets", [])
            visible_sheets = []
            hidden_sheets = []
            for sheet in sheets:
                title = sheet["properties"]["title"]
                is_hidden = sheet["properties"].get("hidden", False)

                if is_hidden:
                    hidden_sheets.append(title)
                else:
                    visible_sheets.append(title)
            return visible_sheets + hidden_sheets
        except HttpError as e:
            return {"error": f"HTTP error: {e}"}
        except Exception as e:
            return {"error": f"Unexpected error: {e}"}

    def get_data_from_link(self, url: str, sheet_name, formatJson=False):
        """
        Lấy dữ liệu từ Google Sheet thông qua URL
        Returns: DataFrame hoặc None nếu có lỗi
        """
        is_valid, sheet_id = self.set_id_from_path_sheet(url)
        
        if not is_valid:
            return None

        try:
            result = self.sheet.get(
                spreadsheetId=sheet_id,
                ranges=sheet_name,
                includeGridData=True
            ).execute()

            values = []
            row_index = 1

            for row in result["sheets"][0]["data"][0]["rowData"]:
                row_values = []
                for cell in row.get("values", []):
                    if "hyperlink" in cell:
                        # Nếu ô có hyperlink, bọc trong thẻ <a>
                        link = cell["hyperlink"]
                        text = cell.get("formattedValue", link)
                        if formatJson:
                            row_values.append({"text": text, "link": link})
                        else:
                            row_values.append(f"<a href='{link}' target='_blank'><i><u>{text}</u></i></a>")
                    else:
                        # Nếu không có link, trả về giá trị bình thường
                        row_values.append(cell.get("formattedValue", ""))
                # print(json.dumps(row_values, indent=4, ensure_ascii=False))

                row_values.append(row_index)  
                if any(cell.strip() if isinstance(cell, str) else str(cell).strip() for cell in row_values[:-1]):  
                    values.append(row_values) 

                row_index += 1

            values = [
                row for row in values
                if any(cell.strip() if isinstance(cell, str) else str(cell) for cell in row)
            ]
            if not values:
                # print("Google Sheet is empty!")
                return {"headers": [], "data": []}

            # Chuyển dữ liệu thành dictionary
            headers = [h for h in values[0] if isinstance(h, str) and h.strip()]
            headers.append("row_id")
            data = [dict(zip(headers, row)) for row in values[1:]]

            return {"headers": headers, "data": data}
        except HttpError as e:
            # print(f"Error when truy cap Google Sheet: {e}")
            return None
        except Exception as e:
            # print(f"Error not found: {e}")
            return None

    def get_service_account_email(self):
        return self.credentials.service_account_email
    
    def update_task_ids(self, sheet_updates):
        """
        Cập nhật task_id cho các hàng trong Google Sheet.
        """
        if not sheet_updates:
            return True

        for id, row in sheet_updates.items():
            try:
                _, main_sheet_id = self.set_id_from_path_sheet(row.get('link'))
                sheet_id = row.get('main_sheet_id')
                updates = row.get('updates')

                if not updates:
                    continue

                data_updates = []
                for up in updates:
                    row_id = up.get('row_id')
                    value = up.get('value')

                    if row_id is not None and value is not None:
                        data_updates.append({
                            "range": f"Tasks!A{row_id}",
                            "values": [[value]]
                        })

                if not data_updates:
                    continue

                body = {
                    'valueInputOption': 'USER_ENTERED',
                    'data': data_updates
                }

                try:
                    self.sheet.values().batchUpdate(spreadsheetId=main_sheet_id, body=body).execute()
                    # print(f"Update success {len(data_updates)} task_id(s) in Google Sheet {main_sheet_id}")
                except Exception as e:
                    Notification.create(
                        title=f"Công ty: {row.get('name')}",
                        content="Không có quyền chỉnh sửa"
                    )
                    # print(f"Error when update Google Sheet {main_sheet_id}: {e}")
            except Exception as e:
                print(f'Error when update: {id}')

        return True


def get_tasks(sheet_name):
    gg_sheet = GoogleSheets()
    data = gg_sheet.get_data_from_link(settings.GOOGLE_SHEET_MAIN_LINK, sheet_name)
    return data

def add_task(sheet_name, task_data):
    try:
        # sheet = get_google_sheet(sheet_name)
        # sheet.append_row([
        #     task_data.get('title', ''),
        #     task_data.get('description', ''),
        #     task_data.get('status', 'New'),
        #     task_data.get('assigned_to', '')
        # ])
        return True
    except Exception as e:
        print(f"Error adding task: {e}")
        return False

def get_sheet_names():
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        settings.CREDENTIALS_PATH,
        scope
    )
    client = gspread.authorize(credentials)
    
    spreadsheet = client.open_by_key(settings.GOOGLE_SHEET_ID)
    return [worksheet.title for worksheet in spreadsheet.worksheets()]