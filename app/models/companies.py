from sqlalchemy import Column, String
from app.models.base import BaseModel, db_session

class Companies(BaseModel):
    __tablename__ = 'companies'
    __fillable__ = ['name', 'sheet_link', 'status', 'comment']
    
    name = Column(String(255), nullable=False)
    sheet_link = Column(String(255), nullable=True)
    status = Column(String(50), default='active')
    comment = Column(String(50), nullable=True)

    @classmethod
    def active(cls):
        """Lấy danh sách công ty đang hoạt động"""
        return db_session.query(cls).filter_by(status='active').all()

    def deactivate(self):
        """Ngừng hoạt động công ty"""
        self.status = 'inactive'
        try:
            db_session.commit()
            return True
        except:
            db_session.rollback()
            return False
