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
    """
    GET-Роутер для получения страницы логина
    :param request: Параметры запроса
    :return: HTML Страница логина
    """
    return templates.TemplateResponse("login.html", {"request": request})


# Логин с JWT
@router.post("/login-jwt")
async def login_for_jwt(
    request: Request,
    user: User = Depends(validate_user),
):
    """
    POST-Роутер для логина с JWT
    При неверных данных возвращаем страницу логина с ошибкой,
    Если пользователь правильно ввел данные, то создаем новый JWT токен и возвращаем страницу профиля
    :param request: Параметры запроса
    :param user: Пользователь полученный из БД
    :return: RedirectResponse
    """

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
    request: Request
):
    """
    GET-Роутер для получения страницы профиля
    :param request: Параметры запроса
    :return: RedirectResponse
    """
    # Проверяем есть ли токен в куках
    token = request.cookies.get("access_jwt_token")
    if not token:
        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={
                "error_message": "Login to your account",
            },
        )
    # Проверяем токен на валидность и получаем данные из него
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
    """
    GET-Роутер для получения страницы со всеми пользователями
    Роутер доступен только для пользователя admin, проверка осуществляется с помощью
    зависимости get_all_users_from_db
    :param request: Параметры запроса
    :param users: Список пользователей
    :return: HTML-страница со всеми пользователями
    """
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
async def logout_user():
    """
    GET-Роутер для выхода из аккаунта
    :return: RedirectResponse
    """
    response = RedirectResponse(url="/login")
    response.delete_cookie(key="access_jwt_token")
    return response


# Регистрация
@router.get("/register")
async def register_page(request: Request):
    """
    GET-Роутер для получения страницы регистрации
    :param request: Параметры запроса
    :return: HTML-страница регистрации
    """
    return templates.TemplateResponse(request=request, name="register.html")


@router.post("/register")
async def register_user(
    request: Request,
    get_db_session: Annotated[Session, Depends(get_db)],
    username: str = Form(),  # Извлекаем username из данных формы
    password: str = Form(),  # Извлекаем password из данных формы
):
    """
    POST-Роутер для регистрации пользователя

    :param request: Параметры запроса
    :param get_db_session: ORM-сессия для работы с БД
    :param username: Имя пользователя
    :param password: Пароль пользователя
    :return:
    """
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
    else:
        context = {"message": "Your registration was failed! Please try again"}
        print(f"Error with registration {username}")
        return templates.TemplateResponse(
            request=request, name="register.html", context=context
        )


@router.get("/")
async def get_home_page(request: Request):
    """
    GET-Роутер для получения главной страницы
    :param request: Параметры запроса
    :return: HTML-шаблон главной страницы
    """
    return templates.TemplateResponse(request=request, name="home.html")
