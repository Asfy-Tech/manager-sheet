from sqlalchemy import Column, String, Text, Boolean
from app.models.base import BaseModel, db_session

# Múi giờ Việt Nam
class Notification(BaseModel):
    __tablename__ = 'notifications'

    __fillable__ = ['title', 'content', 'is_read']

    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)

    @classmethod
    def get_sorted_by_created_at(cls):
        return db_session.query(cls).order_by(cls.created_at.desc()).all()