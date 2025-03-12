from sqlalchemy import Column, String, Boolean, DateTime, Integer, JSON
from datetime import datetime
from typing import List
from sqlalchemy import func
from app.models.base import BaseModel, db_session

class TelegramUser(BaseModel):
    __tablename__ = "telegram_users"
    
    __fillable__: List[str] = ["name", "chat_id", "role"]

    name = Column(String(100))
    chat_id = Column(String(50))
    role = Column(Integer, default=1, comment="1: Quản trị viên, 2: Nhân sự")

    @classmethod
    def find_by_task_and_date(cls, task_id: str, date: datetime.date):
        """Tìm bản ghi theo task_id và ngày created_at."""
        # return db_session.query(cls).filter(
        #     func.date(cls.created_at) == date,
        #     cls.task_id == task_id
        # ).first()
