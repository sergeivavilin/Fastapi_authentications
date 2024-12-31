from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form, status

from fastapi.responses import HTMLResponse

from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from hashlib import sha256

from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

from Session_auth.session_app.database import get_db

from Session_auth.session_app.models import UserSession, User
from Session_auth.session_app.session_router import MAX_SESSIONS_LIFETIME
from Session_auth.session_app.tools import templates, generate_session_token

router = APIRouter(tags=["Authentication"])

# Регистрация
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")


@router.post("/register")
async def register_user(
        request: Request,
        get_db_session: Annotated[Session, Depends(get_db)],
        username: str = Form(),  # Извлекаем username из данных формы
        password: str = Form(),  # Извлекаем password из данных формы
):
    hashed_password = sha256(password.encode()).hexdigest()
    user = get_db_session.scalar(select(User).where(User.username == username))

    if user:
        context={
            "message": "Choose another username",
        }
        return templates.TemplateResponse(request=request, name="register.html", context=context)

    get_db_session.add(User(username=username, password=hashed_password))
    get_db_session.commit()

    context = {
        "message": "You were registered! Please login"
    }

    return templates.TemplateResponse(request=request, name="login.html", context=context)


# Логин
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@router.post("/login")
async def login_user(
        get_db_session: Annotated[Session, Depends(get_db)],
        response: Response,
        request: Request,
        # Извлекаем данные из формы
        username: str = Form(),
        password: str = Form(),
):
    #
    hashed_password = sha256(password.encode()).hexdigest()
    user: User = get_db_session.scalar(select(User).where(User.username == username))
    if not user or user.password != hashed_password:
        context = {
            "message": "Invalid username or password",
        }
        return templates.TemplateResponse(request=request, name="login.html", context=context)

    session_token = generate_session_token()

    # Удаляем старые сессии пользователя из DB
    try:
        get_db_session.execute(delete(UserSession).where(UserSession.user_id == user.id))
        get_db_session.commit()
    except AttributeError as e:
        print(e)

    # Сохраняем новую сессию
    new_session = UserSession(user_id=user.id, session_token=session_token)
    get_db_session.add(new_session)
    get_db_session.commit()


    # response.set_cookie("session_token", session_token, httponly=True)
    response = templates.TemplateResponse(request=request, name="profile.html", context={"user": user})
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,  # Ограничиваем доступ к cookie только через HTTP (не через JS)
        max_age=MAX_SESSIONS_LIFETIME,  # Время жизни куки
        samesite="lax",  # Политика SameSite для защиты от CSRF
        secure=False  # Установить True для HTTPS
    )
    return response
    # return RedirectResponse(url='/profile')
    # return {"message": "Login successful"}


# Logout
@router.get("/logout")
async def logout_user(
        get_db_session: Annotated[Session, Depends(get_db)],
        response: Response,
        request: Request,
):
    session_token = request.cookies.get("session_token")
    print(session_token)
    if session_token:
        get_db_session.execute(delete(UserSession).where(UserSession.session_token == session_token))
        get_db_session.commit()

    # request.session.clear()
    response.delete_cookie(key="session_token")
    return RedirectResponse(url='/')
    # return templates.TemplateResponse(request=request, name="login.html")
    # return {"message": "Logged out successfully", "deleted_token": session_token}

# @router.get("/logout")
# async def logout_user():
#     return RedirectResponse(url='/login')


@router.get("/")
async def home_page(
        request: Request,
):
    return templates.TemplateResponse(request=request, name="home.html")
