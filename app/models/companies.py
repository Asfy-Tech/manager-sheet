from sqlalchemy import Column, String, DateTime
from app.models.base import BaseModel, db_session
from datetime import datetime
import pytz
vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")

class Companies(BaseModel):
    __tablename__ = 'companies'
    __fillable__ = ['name', 'sheet_link', "last_active", 'status', 'comment']
    
    name = Column(String(255), nullable=False)
    sheet_link = Column(String(255), nullable=True)
    status = Column(String(50), default='active')
    last_active = Column(DateTime, default=lambda: datetime.now(vn_tz))
    comment = Column(String(50), nullable=True)

    @classmethod
    def active(cls):
        """Lấy danh sách công ty đang hoạt động"""
        return db_session.query(cls).filter_by(status='active').all()
    
    @classmethod
    def get_sorted_by_last_active(cls):
        return db_session.query(cls).order_by(cls.last_active.asc()).all()

    def deactivate(self):
        """Ngừng hoạt động công ty"""
        self.status = 'inactive'
        try:
            db_session.commit()
            return True
        except:
            db_session.rollback()
            return False
