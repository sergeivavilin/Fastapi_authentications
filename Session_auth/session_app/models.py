from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from Session_auth.session_app.database import Base


class User(Base):
    """
    Базовая модель пользователя
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    # Связь с таблицей Session
    sessions = relationship("UserSession", back_populates="user")


class UserSession(Base):
    """
    Модель сессии пользователя
    """
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    session_token = Column(String, unique=True, nullable=False)

    # Связь с моделью User
    user = relationship("User", back_populates="sessions")
