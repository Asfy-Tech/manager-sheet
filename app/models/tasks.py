from sqlalchemy import Column, String, Text, JSON
from app.models.base import BaseModel, db_session
from typing import List, Dict
from sqlalchemy.dialects.postgresql import JSONB  # Nếu dùng PostgreSQL

class Task(BaseModel):
    __tablename__ = 'tasks'

    task_id = Column(String(100), primary_key=True, unique=True, nullable=False)
    status = Column(String(50), default="pending")
    data = Column(JSON, nullable=True)  # Hoặc JSONB nếu dùng PostgreSQL

    @classmethod
    def create(cls, **kwargs) -> "Task":
        """Tạo mới task"""
        instance = cls(**kwargs)
        db_session.add(instance)
        db_session.commit()
        return instance

    @classmethod
    def first_or_create(cls, task_id: str, **kwargs) -> "Task":
        """Tìm task theo `task_id`, nếu không có thì tạo mới"""
        instance = db_session.query(cls).filter_by(task_id=task_id).first()
        return instance or cls.create(task_id=task_id, **kwargs)

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
        """Thêm hoặc cập nhật nhiều task một lúc (tối ưu hơn)"""
        try:
            existing_tasks = {task.task_id: task for task in db_session.query(cls).filter(
                cls.task_id.in_([t["task_id"] for t in tasks if "task_id" in t])
            ).all()}

            for task_data in tasks:
                task_id = task_data.get("task_id")
                if not task_id:
                    continue
                
                if task_id in existing_tasks:
                    for key, value in task_data.items():
                        setattr(existing_tasks[task_id], key, value)
                else:
                    db_session.add(cls(**task_data))

            db_session.commit()
            return True
        except Exception as e:
            db_session.rollback()
            # print(f"[ERROR] bulk_upsert failed: {e}")
            return False

    def get_status(self) -> str:
        """Lấy trạng thái hiện tại của task"""
        return self.status or "pending"

    def is_completed(self) -> bool:
        """Kiểm tra xem task đã hoàn thành chưa"""
        return self.status == "completed"

    def mark_as_completed(self) -> bool:
        """Đánh dấu task là đã hoàn thành"""
        self.status = "completed"
        try:
            db_session.commit()
            return True
        except:
            db_session.rollback()
            return False

    def get_data(self) -> Dict:
        """Lấy dữ liệu task (trả về `{}` nếu không có)"""
        return self.data if isinstance(self.data, dict) else {}
