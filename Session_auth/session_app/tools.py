import os
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.templating import Jinja2Templates

from Session_auth.db_config import BASE_DIR
from Session_auth.session_app.database import get_db
from Session_auth.session_app.models import UserSession



templates = Jinja2Templates(directory=f"{BASE_DIR}{os.sep}templates")
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