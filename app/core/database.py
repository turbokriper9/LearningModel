from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.core.config import DATABASE_URL, DB_TYPE

# Создаем базовый класс для моделей
Base = declarative_base()

# Создаем движок SQLAlchemy
if DB_TYPE == "sqlite":
    # Для SQLite добавляем параметр check_same_thread=False
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Для MySQL используем стандартные настройки
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,  # Переподключение к серверу через час
        pool_pre_ping=True,  # Проверять соединение перед использованием
    )

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