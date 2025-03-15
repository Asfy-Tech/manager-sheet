from sqlalchemy import Column, String, Text, Boolean, DateTime
from app.models.base import BaseModel, db_session
from datetime import datetime
import pytz

vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")

class Notification(BaseModel):
    __tablename__ = 'notifications'

    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(vn_tz))

    @classmethod
    def get_sorted_by_created_at(cls, descending=True):
        """Lấy danh sách thông báo sắp xếp theo thời gian tạo (mặc định giảm dần)"""
        order = cls.created_at.desc() if descending else cls.created_at.asc()
        return db_session.query(cls).order_by(order).all()

    def mark_as_read(self):
        """Đánh dấu thông báo là đã đọc"""
        if not self.is_read:
            self.is_read = True
            try:
                db_session.commit()
                return True
            except:
                db_session.rollback()
                return False
        return False
