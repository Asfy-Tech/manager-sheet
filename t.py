
# from app.monitors.file_watcher import FileWatcher
# watcher = FileWatcher(interval=30)
# watcher._check_files()

# from app.models.base import Base, engine
from app.models.telegram_message import TelegramMessage
# # # from app.models.telegram_users import TelegramUser
# # # from app.models.users import User
# # # from app.models.companies import Companies
# # # from app.models.notifications import Notification
from app.models.notificationw import Notifications
# Base.metadata.create_all(engine)
# from config import hash_password, check_password
# # # from datetime import datetime

template = Notifications.find(1)
task = TelegramMessage.find(45)
task2 = TelegramMessage.find(46)
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
      }
    ],
    "future": [],
    "is_admin": True
  }
}
from app.services.bot_telegram import BotFather
bot = BotFather()
bot.send_message(5882159790, '<b>Bold</b>', parse_mode="HTML")
bot.send_message(5882159790, '<i>Italic</i>', parse_mode="HTML")
bot.send_message(5882159790, '<u>Underline</u>', parse_mode="HTML")
bot.send_message(5882159790, '<a href="https://example.com">Link</a>', parse_mode="HTML")
bot.send_message(5882159790, '<code>Code</code>', parse_mode="HTML")
bot.send_message(5882159790, '<pre>Preformatted</pre', parse_mode="HTML")
# bot._send_message_for_user(send)