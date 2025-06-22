from sqlalchemy import Column, Integer, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

DATABASE_URL = "sqlite:///attendance.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class AttendanceLog(Base):
    __tablename__ = "attendance_log"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    count = Column(Integer)

# создаёт таблицу, если ещё нет
Base.metadata.create_all(bind=engine)