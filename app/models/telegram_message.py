from sqlalchemy import Column, String, Boolean, DateTime, Integer, JSON
from datetime import datetime
from typing import List
from sqlalchemy import func
from app.models.base import BaseModel, db_session

class TelegramMessage(BaseModel):
    __tablename__ = "telegram_messages"
    
    __fillable__: List[str] = ["task_id", "category", "todo", "representative", "support", "deadline", "delay","is_seen","send_to"]

    task_id = Column(String(50), nullable=False)
    category = Column(String(150), nullable=False, comment="Hạng mục")
    todo = Column(String(200), unique=True, nullable=False, comment="Việc cần làm")
    representative = Column(String(100), comment="Người phụ trách")
    support = Column(String(100), default=True, comment="Người hỗ trợ")
    status = Column(String(255), nullable=True)
    deadline = Column(DateTime, nullable=True)
    delay = Column(Integer, default=0, nullable=True)
    is_seen = Column(Boolean(), default=False)
    type = Column(Integer, default=1, nullable=True, comment="1: Trễ hẹn, 2: Tới deadline: 3: Mai tới deadline")
    send_to = Column(JSON, nullable=True)

    @classmethod
    def find_by_task_and_date(cls, task_id: str, date: datetime.date):
        """Tìm bản ghi theo task_id và ngày created_at."""
        return db_session.query(cls).filter(
            func.date(cls.created_at) == date,
            cls.task_id == task_id
        ).first()
