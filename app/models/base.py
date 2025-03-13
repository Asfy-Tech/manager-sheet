from sqlalchemy import create_engine, Column, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
import pytz
from config.settings import settings
from typing import List, Dict, Any, Optional, TypeVar, Type

# Cấu hình kết nối database
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db_session = scoped_session(SessionLocal)

Base = declarative_base()
T = TypeVar('T', bound='BaseModel')

# Múi giờ Việt Nam
vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")

class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=lambda: datetime.now(vn_tz))
    updated_at = Column(DateTime, default=lambda: datetime.now(vn_tz), onupdate=lambda: datetime.now(vn_tz))

    @classmethod
    def find(cls: Type[T], id: int) -> Optional[T]:
        """Tìm một bản ghi theo ID giống Laravel."""
        return db_session.query(cls).filter_by(id=id).first()

    @classmethod
    def get(cls: Type[T], **kwargs) -> List[T]:
        """Lấy tất cả hoặc truyền điều kiện `where` giống Laravel."""
        query = db_session.query(cls).filter_by(**kwargs) if kwargs else db_session.query(cls)
        return query.all()  # Trả về danh sách object thay vì dict

    @classmethod
    def where(cls: Type[T], **kwargs) -> List[T]:
        """Lọc bản ghi theo điều kiện."""
        return db_session.query(cls).filter_by(**kwargs).all()

    @classmethod
    def first(cls: Type[T], **kwargs) -> Optional[T]:
        """Lấy bản ghi đầu tiên theo điều kiện."""
        return db_session.query(cls).filter_by(**kwargs).first()

    @classmethod
    def create(cls: Type[T], **kwargs) -> T:
        """Tạo bản ghi mới."""
        filtered_data = {k: v for k, v in kwargs.items() if k in getattr(cls, '__fillable__', [])}
        instance = cls(**filtered_data)
        db_session.add(instance)
        try:
            db_session.commit()
            return instance
        except:
            db_session.rollback()
            raise

    def update(self, **kwargs) -> bool:
        """Cập nhật bản ghi."""
        for key, value in kwargs.items():
            if key in getattr(self, '__fillable__', []):
                setattr(self, key, value)
        try:
            db_session.commit()
            return True
        except:
            db_session.rollback()
            return False

    def delete(self) -> bool:
        """Xóa bản ghi."""
        try:
            db_session.delete(self)
            db_session.commit()
            return True
        except:
            db_session.rollback()
            return False
    
    @classmethod
    def delete_all(cls) -> bool:
        """Xóa toàn bộ dữ liệu trong bảng."""
        try:
            db_session.query(cls).delete()
            db_session.commit()
            return True
        except:
            db_session.rollback()
            return False
        
    def save(self):
        """Lưu thay đổi vào database."""
        try:
            db_session.commit()
        except:
            db_session.rollback()
            raise
        
    @classmethod
    def delete_by_id(cls, id: int) -> bool:
        instance = db_session.query(cls).filter_by(id=id).first()
        if not instance:
            return False
        db_session.delete(instance)
        try:
            db_session.commit()
            return True
        except:
            db_session.rollback()
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển model thành dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in getattr(self, 'hidden', [])}
