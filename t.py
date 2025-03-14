# from app.monitors.file_watcher import FileWatcher
# watcher = FileWatcher(interval=30)
# watcher._check_files()

# from app.models.base import Base, engine
# from app.models.telegram_message import TelegramMessage
# from app.models.telegram_users import TelegramUser
from app.models.users import User
# from app.models.companies import Companies
# from app.models.notifications import Notification
# from app.models.tasks import Task
# Base.metadata.create_all(engine)
from config import hash_password
from datetime import datetime

User.create(
    name="Nguyễn Ngọc Hiển",
    email="hiencode",
    password=hash_password("hiencode"),
    role="admin",
    status=True,
    avatar="https://example.com/avatar.jpg",
    last_login=datetime.utcnow()
)
# # admins = TelegramUser.get(role=1)
# # print(len(admins))
