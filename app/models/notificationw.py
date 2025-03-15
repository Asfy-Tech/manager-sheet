from sqlalchemy import Column, String, Text, Integer
from app.models.base import BaseModel, db_session

class Notifications(BaseModel):
    __tablename__ = 'notifications_web'

    __fillable__ = ['title', 'content', 'status']

    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Integer, default=1)  # 1: active, 0: inactive
    
    def get(self):
        """Lấy tất cả thông báo, sắp xếp theo thời gian tạo mới nhất"""
        return db_session.query(Notifications).order_by(Notifications.created_at.desc()).all()
    
    def find(self, id):
        """Tìm thông báo theo ID"""
        return db_session.query(Notifications).filter(Notifications.id == id).first()
    
    def create(self, **kwargs):
        """Tạo thông báo mới"""
        notification = Notifications(**kwargs)
        db_session.add(notification)
        db_session.commit()
        return notification
    
    def update(self, id=None, **kwargs):
        """Cập nhật thông báo"""
        if id:
            notification = self.find(id)
            if not notification:
                return None
        else:
            notification = self
            
        for key, value in kwargs.items():
            if key in self.__fillable__:
                setattr(notification, key, value)
        
        db_session.commit()
        return notification
    
    def delete_by_id(self, id):
        """Xóa thông báo theo ID"""
        notification = self.find(id)
        if notification:
            db_session.delete(notification)
            db_session.commit()
            return True
        return False
    
    def to_dict(self):
        """Chuyển đối tượng thành dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }