from sqlalchemy import Column, Integer, String, Boolean

from JWT_auth.JWT_app.database import BASE


class JWTUser(BASE):
    __tablename__ = "jwt_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)


