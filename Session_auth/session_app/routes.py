from typing import Annotated
from hashlib import sha256

from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from sqlalchemy.orm import Session
from sqlalchemy import select, insert, delete
from starlette.responses import RedirectResponse

from Session_auth.session_app.database import get_db
from Session_auth.session_app.models import User, UserSession
from Session_auth.session_app.tools import verify_session

router = APIRouter(tags=["Session Auth"])
templates = Jinja2Templates(directory="templates")


# Регистрация
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def register_user(
        request: Request,
        get_db_session: Annotated[Session, Depends(get_db)],
        username: str = Form(),  # Извлекаем username из данных формы
        password: str = Form(),  # Извлекаем password из данных формы
):
    hashed_password = sha256(password.encode()).hexdigest()
    user = get_db_session.scalar(select(User).where(User.username == username))

    if user is not None:
        context={
            "message": "Chose another username",
            "request": request,
        }
        return templates.TemplateResponse("register.html", context=context)

    get_db_session.add(User(username=username, password=hashed_password))
    get_db_session.commit()

    # return {"message": "User registered successfully"}
    return RedirectResponse(url='/profile')


# Логин
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


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
        context={
            "message": "Invalid username or password",
            "request": request,
        }
        return templates.TemplateResponse("login.html", context=context)
        # raise HTTPException(status_code=401, detail="Invalid username or password")

    session_token = sha256(f"{username}{password}".encode()).hexdigest()

    # Удаляем старые сессии пользователя из DB
    try:
        get_db_session.execute(delete(UserSession).where(UserSession.user_id == user.id))
    except AttributeError as e:
        print(e)

    # Сохраняем новую сессию
    new_session = UserSession(user_id=user.id, session_token=session_token)
    get_db_session.add(new_session)
    get_db_session.commit()

    response.set_cookie("session_token", session_token, httponly=True)
    return templates.TemplateResponse("welcome.html", {"request": request, "user": user})
    # return RedirectResponse(url='/profile')
    # return {"message": "Login successful"}


# Logout
@router.get("/logout")
async def logout_user():
    return RedirectResponse(url='/login')


@router.post("/logout")
async def logout_user(
        get_db_session: Annotated[Session, Depends(get_db)],
        response: Response,
        request: Request,
):
    session_token = request.cookies.get("session_token")
    if session_token:
        get_db_session.execute(delete(UserSession).where(UserSession.session_token == session_token))
        get_db_session.commit()

    response.delete_cookie("session_token")
    return RedirectResponse(url='/logout')
    # return templates.TemplateResponse("login.html", {"request": request})
    # return {"message": "Logged out successfully", "deleted_token": session_token}


# Пример защищенного маршрута: профиль пользователя
@router.get("/profile")
async def profile(
        response: Response,
        request: Request,
        get_db_session: Annotated[Session, Depends(get_db)],
):
    user = verify_session(request, get_db_session)
    return templates.TemplateResponse("profile.html", {"user": user})
    # return {"id": user.id, "username": user.username}


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


# @router.get("/all_users")
# async def get_all_users(request: Request, get_db_session: Session = Depends(get_db)):
#     user = verify_session(request, get_db_session)
#     # TODO: реализовать проверку на администратора
#     # if user.is_admin:
#     #     pass
#     users = get_db_session.scalars(select(User)).all()
#     return {"users" : users}