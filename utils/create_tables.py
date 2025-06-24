from sqlalchemy import create_engine
from app.core.database import Base
from app.models.student import Student, Attendance
from app.core.config import settings

def create_tables():
    """
    Создание таблиц в базе данных напрямую через SQLAlchemy
    """
    # Создаем движок
    engine = create_engine(settings["DATABASE_URL"])
    
    # Создаем все таблицы
    print("Создаем таблицы в базе данных...")
    Base.metadata.create_all(bind=engine)
    print("Таблицы успешно созданы!")

if __name__ == "__main__":
    create_tables() 