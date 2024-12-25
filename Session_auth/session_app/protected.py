from lib2to3.fixes.fix_input import context
from typing import Annotated

from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.responses import Response

from Session_auth.session_app.database import get_db

from Session_auth.session_app.models import User
from Session_auth.session_app.models import UserSession
from Session_auth.session_app.tools import templates

router = APIRouter(tags=["Protected"])

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


# Пример защищенного маршрута: профиль пользователя
@router.get("/profile")
async def profile(
        response: Response,
        request: Request,
        get_db_session: Annotated[Session, Depends(get_db)],
):
    try:
        user = verify_session(request, get_db_session)
    except HTTPException:
        return templates.TemplateResponse(
            "profile.html",
            context={
                "error_message": "Login into your account",
                "request": request
            }
        )
    return templates.TemplateResponse("profile.html", {"user": user, "request": request})
    # return {"id": user.id, "username": user.username}


@router.get("/all_users")
async def get_all_users(request: Request, get_db_session: Session = Depends(get_db)):
    try:
        admin = verify_session(request, get_db_session)
    except HTTPException:
        return templates.TemplateResponse(
            "all_users.html",
            context={
                "error_message": "Login into admin account",
                "request": request
            }
        )
    # TODO: реализовать проверку на администратора
    # if user.is_admin:
    #     pass
    users = get_db_session.scalars(select(User)).all()
    context = {
        "users": users,
        "request": request,
        "admin": admin
    }
    return templates.TemplateResponse("all_users.html", context)