# import pandas as pd
# import json

# # Chuyển đổi URL thành dạng export CSV
# sheet_id = "1WAHisF6PyTorT0L0Ttu2dSdyM_07W_4PWxWWslghDuU"
# gid = "786220283"
# csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
# def load_sheed(csv_url):
#     df = pd.read_csv(csv_url, header=None)

#     # Lấy hàng đầu tiên làm header
#     headers = df.iloc[0].to_list()  
#     df = df[1:].reset_index(drop=True)  

#     # Tạo dictionary {'name': index_header}
#     header_dict = {col_name: idx for idx, col_name in enumerate(headers)}

#     data = []
#     for index, row in df.iterrows():
#         formatRow = row.to_list()
#         dt = {}
#         for head, idx in header_dict.items():
#             dt[head] = formatRow[idx]
#         data.append(dt)
#     return data

# data = load_sheed(csv_url)
# print(json.dumps(data, indent=4, ensure_ascii=False))

import re
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config.settings import settings

def validate_sheet_url(url: str) -> tuple:
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
        # Initialize credentials
        credentials = service_account.Credentials.from_service_account_file(
            settings.CREDENTIALS_PATH,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        # Build sheets API service
        service = build('sheets', 'v4', credentials=credentials)
        
        # Try to get sheet metadata
        sheet = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        
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

# Test the function
url = 'https://docs.google.com/spreadsheets/d/1n9_26Xa_7StlViy0tT9OysC-tl3bzNVnIbYousGThvA/edit?gid=1386834576#gid=1386834576'
is_valid, sheet_id, message = validate_sheet_url(url)

print(f"URL valid: {is_valid}")
print(f"Sheet ID: {sheet_id}")
print(f"Message: {message}")
