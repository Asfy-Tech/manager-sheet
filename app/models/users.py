from sqlalchemy import Column, String, Boolean, DateTime
from datetime import datetime
from typing import List
from app.models.base import BaseModel, db_session

class User(BaseModel):
    __tablename__ = "users"
    
    __fillable__: List[str] = ["name", "email", "password", "role", "status", "avatar", "last_login"]
    hidden: List[str] = ["password"]

    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), default="user")
    status = Column(Boolean, default=True)
    avatar = Column(String(255), nullable=True)
    last_login = Column(DateTime, nullable=True)
