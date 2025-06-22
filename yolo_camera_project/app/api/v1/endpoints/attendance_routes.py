from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.attendance_db import AttendanceLog, SessionLocal
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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/attendance-log", response_model=AttendanceRead)
def create_attendance(att: AttendanceCreate, db: Session = Depends(get_db)):
    row = AttendanceLog(count=att.count)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

@router.get("/attendance-log", response_model=list[AttendanceRead])
def read_attendance(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(AttendanceLog).order_by(AttendanceLog.timestamp.desc()).offset(skip).limit(limit).all()