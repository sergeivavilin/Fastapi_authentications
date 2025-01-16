from authlib.integrations.base_client import OAuthError
from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.templating import Jinja2Templates

from OAuth2_auth.Oauth_app.tools import oauth_exemple

router = APIRouter()

templates = Jinja2Templates(directory="OAuth2_auth/templates")


@router.get("/")
async def homepage(request: Request):
    """
    GET-Роутер для получения главной страницы
    При наличии пользователя в сессии редирект на страницу профиля пользователя
    :param request: Параметры запроса
    :return: HTML-шаблон главной страницы или редирект на страницу профиля пользователя
    """
    user = request.session.get("user")
    if user:
        return RedirectResponse(url="/protected")

    return templates.TemplateResponse(request, "home.html")


@router.get("/login")
async def login(request: Request):
    """
    GET-Роутер для получения страницы авторизации
    При наличии пользователя в сессии редирект на страницу профиля пользователя
    :param request: Параметры запроса
    :return: Редирект на страницу профиля пользователя после авторизации
    """
    user = request.session.get("user")
    if user:
        return RedirectResponse(url="/protected")
    # Формируем ссылку редиректа для авторизации через провайдера
    redirect_uri = request.url_for("auth")
    # Переходим по роутеру авторизации 'auth' с помощью провайдера
    return await oauth_exemple.google.authorize_redirect(request, redirect_uri)


@router.get("/auth")
async def auth(request: Request):
    """
    GET-Роутер для получения токена авторизации
    При наличии пользователя в сессии редирект на страницу профиля пользователя
    :param request: Параметры запроса
    :return: Редирект на страницу профиля пользователя после авторизации
    """
    user = request.session.get("user")
    if user:
        return RedirectResponse(url="/protected")
    # Получаем токен авторизации с помощью провайдера
    try:
        token = await oauth_exemple.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f"<h1>{error.error}</h1>")
    # Получаем информацию о пользователе из токена авторизации
    user = token.get("userinfo")
    # добавляем информацию о пользователе в сессию пользователя
    if user:
        request.session["user"] = user
    return RedirectResponse(url="/protected")


@router.get("/logout")
async def logout(request: Request):
    """
    GET-Роутер для выхода из аккаунта
    :param request: Параметры запроса
    :return: Редирект на главную страницу
    """
    request.session.pop("user", None)
    return RedirectResponse(url="/")


@router.get("/protected")
async def protected(request: Request):
    """
    GET-Роутер для получения страницы профиля пользователя
    :param request: Параметры запроса
    :return: HTML-шаблон страницы профиля пользователя
    """
    user = request.session.get("user")
    if user:
        context_ = {"user": user}
        return templates.TemplateResponse(request, "protected.html", context=context_)
    return RedirectResponse(url="/")
