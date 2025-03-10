import pandas as pd
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from config.settings import settings
import re
from googleapiclient.errors import HttpError

class GoogleSheets:
    def __init__(self):
        self.credentials = service_account.Credentials.from_service_account_file(
            settings.CREDENTIALS_PATH,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        self.service = build('sheets', 'v4', credentials=self.credentials)
        self.sheet = self.service.spreadsheets()
    

    def validate_sheet_url(self, url: str) -> tuple:
        """
        Validate Google Sheet URL and check if it's accessible
        Returns: (is_valid: bool, sheet_id: str, error_message: str)
        """
        # Extract sheet ID from URL using regex
        pattern = r'/d/([a-zA-Z0-9-_]+)'
        match = re.search(pattern, url)
        
        if not match:
            return False, None, "Invalid Google Sheet URL format"
        
        sheet_id = match.group(1)
        
        try:
            # Try to get sheet metadata
            sheet = self.service.spreadsheets().get(spreadsheetId=sheet_id).execute()
            return True, sheet_id, "Sheet is accessible"
        except HttpError as e:
            if e.resp.status == 403:
                return False, sheet_id, "Permission denied. Make sure the sheet is shared with the service account"
            elif e.resp.status == 404:
                return False, sheet_id, "Sheet not found"
            else:
                return False, sheet_id, f"Error accessing sheet: {str(e)}"
        except Exception as e:
            return False, sheet_id, f"Unexpected error: {str(e)}"
        
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

    def get_data_from_link(self, url: str, sheet_name):
        """
        Lấy dữ liệu từ Google Sheet thông qua URL
        Returns: DataFrame hoặc None nếu có lỗi
        """
        is_valid, sheet_id, message = self.validate_sheet_url(url)
        
        if not is_valid:
            print(f"❌ {message}")
            return None

        try:
            result = self.sheet.values().get(
                spreadsheetId=sheet_id,
                range=sheet_name
            ).execute()

            values = result.get('values', [])

            if not values:
                print("⚠️ Google Sheet trống!")
                return {"headers": [], "data": []}

            # Chuyển dữ liệu thành dictionary
            headers = values[0]
            data = [dict(zip(headers, row)) for row in values[1:]]

            return {"headers": headers, "data": data}
        except HttpError as e:
            print(f"❌ Lỗi khi truy cập Google Sheet: {e}")
            return None
        except Exception as e:
            print(f"❌ Lỗi không xác định: {e}")
            return None


    
    def get_service_account_email(self):
        return self.credentials.service_account_email
    

def get_tasks(sheet_name):
    gg_sheet = GoogleSheets()
    data = gg_sheet.get_data_from_link(settings.GOOGLE_SHEET_MAIN_LINK, sheet_name)
    return data

def add_task(sheet_name, task_data):
    try:
        sheet = get_google_sheet(sheet_name)
        sheet.append_row([
            task_data.get('title', ''),
            task_data.get('description', ''),
            task_data.get('status', 'New'),
            task_data.get('assigned_to', '')
        ])
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