from typing import Annotated, Optional

from fastapi import APIRouter, Request, HTTPException, Depends, Cookie
from sqlalchemy import select
from sqlalchemy.orm import Session

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
    """
    Проверка сессионного токена пользователя.
    Если сессионный токен не найден или не валиден, то возвращается ошибка 401.
    Если сессионный токен валиден, то возвращается пользователь из БД.

    :param get_db_session: ORM-сессия подключения к БД
    :param session_token: сессионный токен пользователя
    :return: пользователь из БД
    """

    if not session_token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    session = get_db_session.scalar(
        select(UserSession).where(UserSession.session_token == session_token)
    )
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    return session.user


@router.get("/profile")
async def profile(
    request: Request,
    get_db_session: Annotated[Session, Depends(get_db)],
    session_token: Optional[str] = Cookie(alias="session_token"),
):
    """
    Пример защищенного маршрута: профиль пользователя.
    Если пользователь не авторизован, то возвращается ошибка 401.
    Если пользователь авторизован, то возвращается шаблон с профилем пользователя.

    :param request: Параметры запроса
    :param get_db_session: ORM-сессия подключения к БД
    :param session_token: сессионный токен пользователя
    :return: HTML-страница с профилем пользователя
    """
    try:
        user = verify_session(get_db_session, session_token)
    except HTTPException:
        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={
                "error_message": "Login to your account",
            },
        )
    return templates.TemplateResponse(
        request=request, name="profile.html", context={"user": user}
    )


@router.get("/all_users")
async def get_all_users(request: Request, get_db_session: Session = Depends(get_db)):
    session_token = request.cookies.get("session_token")
    try:
        admin = verify_session(get_db_session, session_token)
    except HTTPException:
        return templates.TemplateResponse(
            request=request,
            name="all_users.html",
            context={
                "error_message": "Login to admin account",
            },
        )
    # TODO: реализовать проверку на администратора
    # if user.is_admin:
    #     pass
    users = get_db_session.scalars(select(User)).all()
    context = {
        "users": users,
    }
    return templates.TemplateResponse(
        request=request, name="all_users.html", context=context
    )
