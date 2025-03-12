import json
import requests
import threading
from config import settings
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import asyncio

class BotFather:
    def __init__(self):
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def me(self):
        """Lấy thông tin về bot"""
        return self._request("getMe")

    def get_updates(self, offset=None, limit=100, timeout=0):
        """Lấy các cập nhật tin nhắn mới nhất và xử lý lệnh /myid"""
        params = {
            "offset": offset,
            "limit": limit,
            "timeout": timeout
        }
        updates = self._request("getUpdates", params)
        
        if updates.get("result"):
            for update in updates["result"]:
                message = update.get("message", {})
                if "text" in message and message["text"] == "/myid":
                    chat_id = message["chat"]["id"]
                    self.send_message(chat_id, f"Your chat ID is: {chat_id}")
        return updates

    def send_message(self, chat_id, text, parse_mode="HTML"):
        """Gửi tin nhắn đến một chat_id"""
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        return self._request("sendMessage", payload)

    def send_photo(self, chat_id, photo_url, caption=None):
        """Gửi ảnh đến một chat_id"""
        payload = {
            "chat_id": chat_id,
            "photo": photo_url,
            "caption": caption
        }
        return self._request("sendPhoto", payload)

    def send_audio(self, chat_id, audio_url, caption=None):
        """Gửi âm thanh đến một chat_id"""
        payload = {
            "chat_id": chat_id,
            "audio": audio_url,
            "caption": caption
        }
        return self._request("sendAudio", payload)

    def pin_message(self, chat_id, message_id):
        """Ghim một tin nhắn trong nhóm chat"""
        payload = {"chat_id": chat_id, "message_id": message_id}
        return self._request("pinChatMessage", payload)

    def unpin_message(self, chat_id, message_id):
        """Gỡ ghim một tin nhắn trong nhóm chat"""
        payload = {"chat_id": chat_id, "message_id": message_id}
        return self._request("unpinChatMessage", payload)

    def delete_message(self, chat_id, message_id):
        """Xóa một tin nhắn trong nhóm chat"""
        payload = {"chat_id": chat_id, "message_id": message_id}
        return self._request("deleteMessage", payload)

    def get_chat_members(self, chat_id):
        """Lấy danh sách các thành viên trong một nhóm chat"""
        payload = {"chat_id": chat_id}
        return self._request("getChatMembersCount", payload)

    def get_chat_info(self, chat_id):
        """Lấy thông tin về một nhóm chat"""
        payload = {"chat_id": chat_id}
        return self._request("getChat", payload)

    def get_chat_member(self, chat_id, user_id):
        """Lấy thông tin về thành viên trong nhóm chat"""
        payload = {"chat_id": chat_id, "user_id": user_id}
        return self._request("getChatMember", payload)

    def get_chat_administrators(self, chat_id):
        """Lấy danh sách quản trị viên trong nhóm chat"""
        payload = {"chat_id": chat_id}
        return self._request("getChatAdministrators", payload)

    def get_chat_pinned_message(self, chat_id):
        """Lấy thông tin tin nhắn ghim trong nhóm chat"""
        payload = {"chat_id": chat_id}
        return self._request("getChatPinnedMessage", payload)

    def _request(self, method, payload=None):
        """Hàm hỗ trợ thực hiện các yêu cầu API"""
        url = f"{self.base_url}/{method}"
        try:
            response = requests.post(url, json=payload) if payload else requests.get(url, params=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    def send_multiple_tasks(self, tasks):
        late = tasks.get('late')
        today = tasks.get('today')
        future = tasks.get('future')
        self.dd(tasks)

    def dd(self, data):
        """In ra dữ liệu dưới dạng JSON đẹp"""
        print(json.dumps(data, indent=4, ensure_ascii=False))

    # Hàm để xử lý lệnh /my_id
    async def my_id(self, update: Update, context: CallbackContext) -> None:
        """Trả về chat_id của người dùng"""
        chat_id = update.message.chat_id
        await update.message.reply_text(f"Your chat ID is: {chat_id}")

    def start_bot(self):
        """Khởi động bot và thêm CommandHandler"""
        # Sử dụng Application 
        application = Application.builder().token(self.token).build()

        # Thêm handler cho lệnh /myid
        application.add_handler(CommandHandler("myid", self.my_id))

        # Tạo event loop cho thread hiện tại
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Bắt đầu bot
        application.run_polling()

bot = BotFather()
def run_bot_in_thread():
    bot_instance = BotFather()
    """Chạy bot Telegram trong một thread riêng biệt"""
    bot_thread = threading.Thread(target=bot_instance.start_bot)
    bot_thread.daemon = True  # Cho phép thread tự tắt khi chương trình chính kết thúc
    bot_thread.start()
