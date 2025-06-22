from sqlalchemy import Column, Integer, String, DateTime, func
from datetime import datetime
from app.core.database import Base

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    group = Column(String(50))

class Attendance(Base):
    """
    Модель для хранения данных о посещаемости аудитории
    """
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    count = Column(Integer)
    
    def to_dict(self):
        """
        Преобразует запись в словарь для API
        """
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "count": self.count
        }