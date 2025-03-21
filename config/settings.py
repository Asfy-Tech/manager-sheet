import os
from pathlib import Path
from dotenv import load_dotenv

class Settings:
    # Load environment variables
    load_dotenv()

    # Main ID Admin
    ADMIN_ID = os.getenv('ADMIN_ID', '1')
    
    # Base paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    APP_DIR = BASE_DIR / "app"
    
    # App directories
    STATIC_DIR = BASE_DIR / "static"
    LOGS_DIR = BASE_DIR / "logs"
    TEMPLATES_DIR = APP_DIR / "web" / "templates"
    
    # Create required directories
    for directory in [LOGS_DIR, TEMPLATES_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    
    # Database settings
    DATABASE_PATH = BASE_DIR / "database.db"
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '3306')
    DB_NAME = os.getenv('DB_NAME', 'manager_sheets')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASS = os.getenv('DB_PASS', '')
    
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # App Key
    APP_KEY = os.getenv('APP_KEY', '')

    # Google settings
    GOOGLE_SHEET_MAIN_LINK = os.getenv("GOOGLE_SHEET_MAIN_LINK")
    MAIN_SHEET_ID = os.getenv("MAIN_SHEET_ID")
    CREDENTIALS_PATH = BASE_DIR / "credentials.json"
    
    # Monitoring settings
    SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", "60"))
    
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7018095153:AAFzuT3T8nU1l1lN7bZ6n5geq1R0kNtkMYQ")

    # Logging
    LOG_FILE = LOGS_DIR / "file_changes.log"

    # Tasks
    TASK_ID = 'TASK_ID'
    TASK_STATUS = 'TRẠNG THÁI'
    TASK_DEADLINE = 'DEADLINE'
    TASK_FINISH_DATE = 'THỜI GIAN HOÀN THÀNH'
    TASK_USER = 'PHỤ TRÁCH'
    TASK_STATUS_SUCCESS = 'Ðã hoàn thành'

    # Upload
    UPLOAD_FOLDER = BASE_DIR / "static/uploads"

    TEMPLATE_FILE = BASE_DIR / "message_template.txt"
    TEMPLATE_DEFAULT_FILE = BASE_DIR / "config/default_template.txt"
    

settings = Settings()