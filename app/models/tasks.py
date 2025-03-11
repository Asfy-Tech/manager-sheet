from sqlalchemy import Column, String, Text, JSON
from app.models.base import BaseModel, db_session
from typing import Optional, List, Dict

class Task(BaseModel):
    __tablename__ = 'tasks'

    task_id = Column(String(100), unique=True, nullable=False)
    status = Column(String(50))
    data = Column(JSON, nullable=True)

    @classmethod
    def first_or_create(cls, task_id: str, **kwargs) -> "Task":
        """Tìm task theo `task_id`, nếu không có thì tạo mới"""
        instance = db_session.query(cls).filter_by(task_id=task_id).first()
        if not instance:
            instance = cls.create(task_id=task_id, **kwargs)
        return instance

    @classmethod 
    def update_or_create(cls, task_id: str, **kwargs) -> "Task":
        """Cập nhật task nếu tồn tại, ngược lại tạo mới"""
        instance = db_session.query(cls).filter_by(task_id=task_id).first()
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            db_session.commit()
        else:
            instance = cls.create(task_id=task_id, **kwargs)
        return instance

    @classmethod
    def bulk_upsert(cls, tasks: List[Dict]) -> bool:
        """Thêm hoặc cập nhật nhiều task một lúc"""
        try:
            for task_data in tasks:
                task_id = task_data.get('task_id')
                if not task_id:
                    continue
                    
                cls.update_or_create(task_id=task_id, **task_data)
                
            db_session.commit()
            return True
        except Exception as e:
            db_session.rollback()
            print(f"[ERROR] bulk_upsert failed: {e}")
            return False

    def get_status(self) -> str:
        """Lấy trạng thái hiện tại của task"""
        return self.status or 'pending'

    def is_completed(self) -> bool:
        """Kiểm tra xem task đã hoàn thành chưa"""
        return self.status == 'completed'

    def mark_as_completed(self) -> bool:
        """Đánh dấu task là đã hoàn thành"""
        return self.update(status='completed')

    def get_data(self) -> Dict:
        """Lấy dữ liệu task (trả về `{}` nếu không có)"""
        return self.data or {}
