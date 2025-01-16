from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from Session_auth.db_config import SQLALCHEMY_DATABASE_URL

# Создаем подключение к БД
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency для получения сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
