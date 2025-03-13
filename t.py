from app.monitors.file_watcher import FileWatcher
watcher = FileWatcher(interval=30)
watcher._check_files()

# from app.models.base import Base, engine
# from app.models.telegram_message import TelegramMessage
# from app.models.telegram_users import TelegramUser
# from app.models.users import User
# from app.models.companies import Companies
# from config import hash_password
# from datetime import datetime
# Base.metadata.create_all(engine)

# User.create(
#     name="Phạm Văn Hùng",
#     email="supperment",
#     password=hash_password("hungpv"),
#     role="admin",
#     status=True,
#     avatar="https://example.com/avatar.jpg",
#     last_login=datetime.utcnow()

# )
# admins = TelegramUser.get(role=1)
# print(len(admins))