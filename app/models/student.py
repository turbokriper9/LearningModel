from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    group = Column(String)

class Attendance(Base):
    """
    Модель для хранения данных о посещаемости аудитории
    """
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
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