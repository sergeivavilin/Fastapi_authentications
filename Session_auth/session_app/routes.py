from hashlib import sha256
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, Form
from fastapi.responses import HTMLResponse
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from Session_auth.session_app.database import get_db
from Session_auth.session_app.models import UserSession, User
from Session_auth.session_app.tools import (
    templates,
    generate_session_token,
    MAX_SESSIONS_LIFETIME,
)

# Создаем роутер для аутентификации
router = APIRouter(tags=["Authentication"])


# Регистрация
@router.get("/register", response_class=HTMLResponse)
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
    username: str = Form(),
    password: str = Form(),
):
    """
    POST-Роутер для регистрации пользователя
    Если юзер уже зарегистрирован, то возвращаем страницу регистрации
    Если юзер не зарегистрирован, то сохраняем его в БД и возвращаем страницу логина

    :param request:  Параметры запроса
    :param get_db_session: ORM-сессия подключения к БД
    :param username: username из данных формы
    :param password: password из данных формы
    :return: HTML-страница регистрации
    """
    hashed_password = sha256(password.encode()).hexdigest()

    # Проверяем наличие ученых данных
    user = get_db_session.scalar(select(User).where(User.username == username))
    if user:
        context = {
            "message": "Choose another username",
        }
        return templates.TemplateResponse(
            request=request, name="register.html", context=context
        )

    # Сохраняем пользователя в БД
    get_db_session.add(User(username=username, password=hashed_password))
    get_db_session.commit()

    context = {"message": "You were registered! Please login"}
    return templates.TemplateResponse(
        request=request, name="login.html", context=context
    )


# Логин
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    GET-Роутер для получения страницы логина
    :param request: Параметры запроса
    :return: HTML-страница логина
    """
    return templates.TemplateResponse(request=request, name="login.html")


@router.post("/login")
async def login_user(
    get_db_session: Annotated[Session, Depends(get_db)],
    request: Request,
    # Извлекаем данные из формы
    username: str = Form(),
    password: str = Form(),
):
    """
    POST-Роутер для логина пользователя.
    При неверных данных возвращаем страницу логина с ошибкой,
    Если пользователь правильно ввел данные, то создаем новый сессионный токен в БД и возвращаем страницу профиля
    :param get_db_session: ORM-сессия подключения к БД
    :param request: Параметры запроса
    :param username: username из данных формы
    :param password: password из данных формы
    :return: HTML-страница профиля
    """

    hashed_password = sha256(password.encode()).hexdigest()

    # Валидируем пользователя
    user: User = get_db_session.scalar(select(User).where(User.username == username))
    if not user or user.password != hashed_password:
        context = {
            "message": "Invalid username or password",
        }
        return templates.TemplateResponse(
            request=request, name="login.html", context=context
        )

    # Генерируем токен сессии
    session_token = generate_session_token()

    # Удаляем старые сессии пользователя из БД
    try:
        get_db_session.execute(
            delete(UserSession).where(UserSession.user_id == user.id)
        )
        get_db_session.commit()
    except AttributeError as e:
        print(e)

    # Сохраняем новую сессию в БД
    new_session = UserSession(user_id=user.id, session_token=session_token)
    get_db_session.add(new_session)
    get_db_session.commit()

    # Создаем шаблон ответа и устанавливаем токен в куки
    response = templates.TemplateResponse(
        request=request, name="profile.html", context={"user": user}
    )
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,  # Ограничиваем доступ к cookie только через HTTP (не через JS)
        max_age=MAX_SESSIONS_LIFETIME,  # Время жизни куки
        samesite="lax",  # Политика SameSite для защиты от CSRF
        secure=False,  # Установить True для HTTPS
    )
    return response


# Logout
@router.get("/logout")
async def logout_user(
    get_db_session: Annotated[Session, Depends(get_db)],
    response: Response,
    request: Request,
):
    """
    GET-Роутер для выхода из аккаунта
    Удаляем токен из БД и удаляем его из куки пользователя и переадресовываем на главную страницу
    :param get_db_session: ORM-сессия подключения к БД
    :param response: Ответ
    :param request: Параметры запроса
    :return: Главная HTML-страница
    """
    # Запрашиваем токен из куки
    session_token = request.cookies.get("session_token")

    # Удаляем токен из БД
    if session_token:
        get_db_session.execute(
            delete(UserSession).where(UserSession.session_token == session_token)
        )
        get_db_session.commit()

    response.delete_cookie(key="session_token")
    return RedirectResponse(url="/")


@router.get("/")
async def home_page(
    request: Request,
):
    """
    GET-Роутер для получения главной страницы
    :param request: Параметры запроса
    :return: HTML-страница главной страницы
    """
    return templates.TemplateResponse(request=request, name="home.html")
