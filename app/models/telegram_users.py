from sqlalchemy import Column, String, Integer
from typing import List
from app.models.base import BaseModel, db_session

class TelegramUser(BaseModel):
    __tablename__ = "telegram_users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    chat_id = Column(String(50), unique=True, nullable=False)
    role = Column(Integer, default=1, comment="1: Quản trị viên, 2: Nhân sự")

    __fillable__: List[str] = ["name", "chat_id", "role"]

    @classmethod
    def find_by_chat_id(cls, chat_id: str):
        """Tìm user theo chat_id."""
        return db_session.query(cls).filter_by(chat_id=chat_id).first()
