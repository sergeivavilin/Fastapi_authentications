import os
import secrets
from hashlib import sha256
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

from Session_auth.db_config import BASE_DIR
from Session_auth.session_app.database import get_db
from Session_auth.session_app.models import UserSession

# Базовый путь к шаблонам
templates = Jinja2Templates(directory=f"{BASE_DIR}{os.sep}templates")

# Время жизни сессии пользователя в секундах
MAX_SESSIONS_LIFETIME = 360  #


# Хелпер для генерации токена сессии
def generate_session_token() -> str:
    token = secrets.token_hex(16)
    return token


# Проверка авторизации
def get_verify_session(
    session_token: str,
    get_db_session: Annotated[Session, Depends(get_db)],
):
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    session = get_db_session.scalar(
        select(UserSession).where(UserSession.session_token == session_token)
    )

    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    return session.user


def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()
