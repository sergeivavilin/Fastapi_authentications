from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from JWT_auth.JWT_app.tools import (
    create_access_token,
    get_all_users_from_db,
    validate_user,
    verify_access_token,
    templates,
    create_user,
)
from Session_auth.session_app.database import get_db
from Session_auth.session_app.models import User

router = APIRouter(tags=["JWT auth"])


@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Логин с JWT
@router.post("/login-jwt")
async def login_for_jwt(
    request: Request,
    user: User = Depends(validate_user),
):
    if not user:
        context = {
            "message": "Invalid username or password",
        }
        return templates.TemplateResponse(
            request=request, name="login.html", context=context
        )

    # Генерация токена
    access_token = create_access_token(
        payload={
            "sub": f"{user.id}",
            "username": f"{user.username}",
        },
    )
    response = RedirectResponse(url="/profile", status_code=302)
    response.set_cookie(
        key="access_jwt_token",
        value=access_token,
        httponly=True,
        # max_age=MAX_JWT_ACCESS_LIFETIME * 60,  # Можно настроить время жизни токена через куки
    )

    return response


@router.get("/profile")
async def get_profile(
    request: Request,
    # access_jwt_token: Optional[str] = Cookie(alias="access_jwt_token")
):
    token = request.cookies.get("access_jwt_token")
    if not token:
        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={
                "error_message": "Login to your account",
            },
        )

    try:
        valid_payload = verify_access_token(token)
    except HTTPException:
        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={
                "error_message": "Login to your account",
            },
        )
    username = valid_payload["username"]
    user_id = valid_payload["sub"]
    context = {"username": username, "user_id": user_id}

    return templates.TemplateResponse(
        request=request, name="profile.html", context=context
    )


@router.get("/all_users")
async def get_all_users(
    request: Request,
    users: list[User] = Depends(get_all_users_from_db),
):
    token = request.cookies.get("access_jwt_token")
    if not token:
        context = {
            "error_message": f"You are not authorized to access this page",
        }
        return templates.TemplateResponse(
            request=request, name="all_users.html", context=context
        )
    try:
        payload = verify_access_token(token)
    except HTTPException as e:
        context = {
            "error_message": f"You are not authorized to access this page",
        }
        return templates.TemplateResponse(
            request=request, name="all_users.html", context=context
        )

    username = payload["username"]
    if username == "admin":
        context = {
            "users": users,
        }
        return templates.TemplateResponse(
            request=request, name="all_users.html", context=context
        )

    context = {
        "error_message": f"You are not authorized to access this page",
    }
    return templates.TemplateResponse(
        request=request, name="all_users.html", context=context
    )


# Logout
@router.get("/logout")
async def logout_user(
    response: Response,
    request: Request,
):
    response = RedirectResponse(url="/login")
    # response.set_cookie(key="access_jwt_token", value="", httponly=True, max_age=10)
    response.delete_cookie(key="access_jwt_token")
    return response


# Регистрация
@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")


@router.post("/register")
async def register_user(
    request: Request,
    get_db_session: Annotated[Session, Depends(get_db)],
    username: str = Form(),  # Извлекаем username из данных формы
    password: str = Form(),  # Извлекаем password из данных формы
):
    user = get_db_session.scalar(select(User).where(User.username == username))
    if user:
        context = {
            "message": "Choose another username",
        }
        return templates.TemplateResponse(
            request=request, name="register.html", context=context
        )

    # Сохраняем пользователя в БД
    if create_user(get_db_session, username, password):
        context = {"message": "You were registered! Please login"}
        return templates.TemplateResponse(
            request=request, name="login.html", context=context
        )


@router.get("/")
async def get_home_page(request: Request):
    return templates.TemplateResponse(request=request, name="home.html")
