from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.requests import Request

from Session_auth.session_app.database import get_db
from Session_auth.session_app.models import UserSession


# Проверка авторизации
def verify_session(
        request: Request,
        get_db_session: Annotated[Session, Depends(get_db)],
):
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    session = get_db_session.scalar(select(UserSession).where(UserSession.session_token == session_token))
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    return session.user
