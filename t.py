
# from app.services.google_sheets import GoogleSheets
# from app.monitors.file_watcher import FileWatcher
# watcher = FileWatcher(interval=30)
# watcher._check_files(GoogleSheets())

from app.models.base import Base, engine
from app.models.telegram_message import TelegramMessage
# from app.models.telegram_users import TelegramUser
# from app.models.users import User
# from app.models.tasks import Task
from app.models.companies import Companies
# from app.models.notifications import Notification
# from app.models.notificationw import Notifications
Base.metadata.create_all(engine)
# from config import hash_password, check_password
# from datetime import datetime

# User.create(
#   name='Trần Văn Hưng',
#   email='hungtv',
#   password=hash_password('12345678'), 
#   role='admin',
#   status=True,
#   avatar='https://static-00.iconduck.com/assets.00/avatar-default-symbolic-icon-479x512-n8sg74wg.png',
#   last_login=datetime.now()
# )

# template = Notifications.find(1)
task = TelegramMessage.find(52)
task2 = TelegramMessage.find(53)
send = {
  "HUNGPV_MKT": {
    "late": [
      {
        "task": task,
        "sheet": {
          "TASK_ID": "TASK_e666a28c",
          "HẠNG MỤC": "Thiết kế các ấn phẩm của Marketing",
          "VIỆC CẦN LÀM": "Helo san pham 123",
          "YÊU CẦU CÔNG VIỆC": "Hội hoa xen ",
          "PHỤ TRÁCH": "HUNGPV_MKT",
          "HỖ TRỢ": "CRYSTAL SPOON",
          "TRẠNG THÁI": "Đang thực hiện",
          "START": "",
          "DEADLINE": "07/03/2025",
          "THÀNH PHẨM": "",
          "DUYỆT": "FALSE",
          "GHI CHÚ": "",
          "CÔNG TY": "Add Today CT"
        }
      }
    ],
    "today": [
      {
        "task": task2,
        "sheet": {
          "TASK_ID": "TASK_8f25a489",
          "HẠNG MỤC": "Tạo hiệu ứng đám đông",
          "VIỆC CẦN LÀM": "Booking Review",
          "YÊU CẦU CÔNG VIỆC": "Tạo hiệu ứng trên facebook bằng cách book bài đăng đến từ những fb nhiều tương tác bạn bè thật.",
          "PHỤ TRÁCH": "QUOC_APK",
          "HỖ TRỢ": "",
          "TRẠNG THÁI": "Tạm hoãn",
          "START": "",
          "DEADLINE": "14/03/2025",
          "THÀNH PHẨM": "",
          "DUYỆT": "",
          "GHI CHÚ": "",
          "CÔNG TY": "Add Today CT"
        }
      },
      {
        "task": task2,
        "sheet": {
          "TASK_ID": "TASK_8f25a489",
          "HẠNG MỤC": "Tạo hiệu ứng đám đông",
          "VIỆC CẦN LÀM": "Booking Review",
          "YÊU CẦU CÔNG VIỆC": " thật.",
          "PHỤ TRÁCH": "QUOC_APK",
          "HỖ TRỢ": "",
          "TRẠNG THÁI": "Tạm hoãn",
          "START": "",
          "DEADLINE": "14/03/2025",
          "THÀNH PHẨM": "",
          "DUYỆT": "",
          "GHI CHÚ": "",
          "CÔNG TY": "CÔNG TY B"
        }
      },
      {
        "task": task2,
        "sheet": {
          "TASK_ID": "TASK_8f25a489",
          "HẠNG MỤC": "Tạo hiệu ứng đám đông",
          "VIỆC CẦN LÀM": "Booking Review",
          "YÊU CẦU CÔNG VIỆC": "Tạo hiệu ứng trên facebook bằng cách book bài đăng đến từ những fb nhiều tương tác bạn bè thật.",
          "PHỤ TRÁCH": "Ninh Loan",
          "HỖ TRỢ": "",
          "TRẠNG THÁI": "Tạm hoãn",
          "START": "",
          "DEADLINE": "14/03/2025",
          "THÀNH PHẨM": "",
          "DUYỆT": "",
          "GHI CHÚ": "",
          "CÔNG TY": "Add Today CT"
        }
      },
      {
        "task": task,
        "sheet": {
          "TASK_ID": "TASK_8f25a489",
          "HẠNG MỤC": "Tạo hiệu ứng đám đông",
          "VIỆC CẦN LÀM": "Booking Review",
          "YÊU CẦU CÔNG VIỆC": "Tạo hiệu ứng trên facebook bằng cách book bài đăng đến từ những fb nhiều tương tác bạn bè thật.",
          "PHỤ TRÁCH": "QUOC_APK",
          "HỖ TRỢ": "",
          "TRẠNG THÁI": "Tạm hoãn",
          "START": "",
          "DEADLINE": "14/03/2025",
          "THÀNH PHẨM": "",
          "DUYỆT": "",
          "GHI CHÚ": "",
          "CÔNG TY": "Add Today CT"
        }
      }
    ],
    "future": [],
    "is_admin": True
  }
}
from app.services.bot_telegram import BotFather
bot = BotFather()
bot._send_message_for_user(send)
