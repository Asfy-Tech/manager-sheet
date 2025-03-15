from sqlalchemy import Column, String, Text, Integer
from app.models.base import BaseModel, db_session

class Notifications(BaseModel):
    __tablename__ = 'notifications_web'

    fillable = ['title', 'content', 'status']

    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Integer, default=1)  # 1: active, 0: inactive