from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.student import Attendance
from pydantic import BaseModel
import datetime

router = APIRouter()

class AttendanceCreate(BaseModel):
    count: int

class AttendanceRead(BaseModel):
    id: int
    timestamp: datetime.datetime
    count: int

    class Config:
        orm_mode = True

@router.post("/attendance", response_model=AttendanceRead)
def create_attendance(att: AttendanceCreate, db: Session = Depends(get_db)):
    """
    Создать новую запись о посещаемости
    """
    row = Attendance(count=att.count)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

@router.get("/attendance", response_model=list[AttendanceRead])
def read_attendance(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Получить историю посещаемости
    """
    return db.query(Attendance).order_by(Attendance.timestamp.desc()).offset(skip).limit(limit).all()