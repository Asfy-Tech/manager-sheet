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
        return db_session.query(cls).filter_by(id=id).first()

    @classmethod
    def get(cls: Type[T], **kwargs) -> List[T]:
        return db_session.query(cls).filter_by(**kwargs).all()

    @classmethod
    def where(cls: Type[T], **kwargs) -> List[T]:
        return db_session.query(cls).filter_by(**kwargs).all()

    @classmethod
    def first(cls: Type[T], **kwargs) -> Optional[T]:
        return db_session.query(cls).filter_by(**kwargs).first()

    @classmethod
    def create(cls: Type[T], **kwargs) -> Optional[T]:
        """Tạo bản ghi mới và commit vào DB"""
        try:
            instance = cls(**kwargs)
            db_session.add(instance)
            db_session.commit()
            return instance
        except Exception as e:
            db_session.rollback()
            print(f"Error creating {cls.__name__}: {e}")
            return None

    def update(self, **kwargs) -> bool:
        """Cập nhật bản ghi và commit"""
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            db_session.commit()
            return True
        except Exception as e:
            db_session.rollback()
            print(f"Error updating {self.__class__.__name__}: {e}")
            return False

    def delete(self) -> bool:
        """Xóa bản ghi khỏi database"""
        try:
            db_session.delete(self)
            db_session.commit()
            return True
        except Exception as e:
            db_session.rollback()
            print(f"Error deleting {self.__class__.__name__}: {e}")
            return False

    @classmethod
    def delete_all(cls) -> bool:
        """Xóa toàn bộ dữ liệu trong bảng"""
        try:
            db_session.query(cls).delete()
            db_session.commit()
            return True
        except Exception as e:
            db_session.rollback()
            print(f"Error deleting all {cls.__name__} records: {e}")
            return False

    def save(self):
        """Lưu thay đổi vào database"""
        try:
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            print(f"Error saving {self.__class__.__name__}: {e}")

    @classmethod
    def delete_by_id(cls, id: int) -> bool:
        instance = cls.find(id)
        if not instance:
            return False
        return instance.delete()

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển model thành dictionary"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in getattr(self, 'hidden', [])}
