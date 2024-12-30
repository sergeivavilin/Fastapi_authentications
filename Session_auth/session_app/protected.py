from typing import Annotated, Optional

from fastapi import APIRouter, Request, HTTPException, Depends, Cookie
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.responses import Response, RedirectResponse

from Session_auth.session_app.database import get_db

from Session_auth.session_app.models import User
from Session_auth.session_app.models import UserSession
from Session_auth.session_app.tools import templates

router = APIRouter(tags=["Protected"])

# Проверка авторизации
def verify_session(
        get_db_session: Annotated[Session, Depends(get_db)],
        session_token: Optional[str] = Cookie(None),
):

    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    session = get_db_session.scalar(select(UserSession).where(UserSession.session_token == session_token))
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    return session.user


# Пример защищенного маршрута: профиль пользователя
@router.get("/profile")
async def profile(
        request: Request,
        get_db_session: Annotated[Session, Depends(get_db)],
        session_token: Optional[str] = Cookie(alias="session_token"),
):
    try:
        user = verify_session(get_db_session, session_token)
    except HTTPException:
        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={
                "error_message": "Login into your account",
            }
        )
    return templates.TemplateResponse(request=request, name="profile.html", context={"user": user})
    # return {"id": user.id, "username": user.username}


@router.get("/all_users")
async def get_all_users(
        request: Request,
        get_db_session: Session = Depends(get_db)
):
    session_token = request.cookies.get("session_token")
    try:
        admin = verify_session(get_db_session, session_token)
    except HTTPException:
        return templates.TemplateResponse(
            request=request,
            name="all_users.html",
            context={
                "error_message": "Login into admin account",
            }
        )
    # TODO: реализовать проверку на администратора
    # if user.is_admin:
    #     pass
    users = get_db_session.scalars(select(User)).all()
    context = {
        "users": users,
    }
    return templates.TemplateResponse(request=request, name="all_users.html", context=context)