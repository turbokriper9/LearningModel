from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import DATABASE_URL

# Создаем базовый класс для моделей
Base = declarative_base()

# Создаем движок SQLAlchemy для MySQL
# Удаляем параметр connect_args={"check_same_thread": False}, так как он нужен только для SQLite
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Функция-зависимость для FastAPI, которая создает и закрывает сессию БД
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Инициализация базы данных - создание таблиц
    """
    Base.metadata.create_all(bind=engine)