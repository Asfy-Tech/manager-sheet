import os
from pathlib import Path
from dotenv import load_dotenv

class Settings:
    # Load environment variables
    load_dotenv()
    
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
    
    # Google settings
    GOOGLE_SHEET_MAIN_LINK = os.getenv("GOOGLE_SHEET_MAIN_LINK")
    SHEET_GID = os.getenv("SHEET_GID")
    CREDENTIALS_PATH = BASE_DIR / "credentials.json"
    
    # Monitoring settings
    SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", "5"))
    
    # Logging
    LOG_FILE = LOGS_DIR / "file_changes.log"

settings = Settings()