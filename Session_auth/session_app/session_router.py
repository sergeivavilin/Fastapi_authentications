import secrets
from fastapi import APIRouter, Depends, Response, HTTPException, Cookie, Form
from hashlib import sha256
from typing import Optional, Annotated, Union

from fastapi.security import HTTPBasicCredentials, HTTPBasic
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, insert, update
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, HTMLResponse

from Session_auth.session_app.database import get_db
from Session_auth.session_app.models import UserSession, User
from Session_auth.session_app.tools import templates, get_verify_session, generate_session_token

router = APIRouter(tags=["Cookie session"])
MAX_SESSIONS_LIFETIME = 180 #

# Логин
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@router.post("/login")
def login_(
        get_db_session: Annotated[Session, Depends(get_db)],
        response: Response,
        request: Request,
        username: str = Form(),
        password: str = Form(),

):

    hashed_password = sha256(password.encode()).hexdigest()

    # Проверяем пользователя
    user: User = get_db_session.scalar(select(User).where(User.username == username))
    if not user or user.password != hashed_password:
        # raise HTTPException(status_code=401, detail="Invalid username or password")
        context = {
            "message": "Invalid username or password",
        }
        return templates.TemplateResponse(request=request, name="login.html", context=context)

    # Генерируем токен сессии
    session_token = generate_session_token()
    response = templates.TemplateResponse("profile.html", {"request": request,"user": user})
    # Устанавливаем токен в куки
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,  # Ограничиваем доступ к cookie только через HTTP (не через JS)
        max_age=MAX_SESSIONS_LIFETIME,  # Время жизни куки
        samesite="lax",  # Политика SameSite для защиты от CSRF
        secure=False  # Установить True для HTTPS
    )

    # Удаляем невалидные сессии
    get_db_session.execute(delete(UserSession).where(UserSession.user_id == user.id))
    get_db_session.commit()

    # Сохраняем новую сессию
    new_session = UserSession(user_id=user.id, session_token=session_token)
    get_db_session.add(new_session)
    get_db_session.commit()

    return response
    # return RedirectResponse(url="/profile")
    # return {"username": user.username, "message": "Welcome to your profile"}
    # return templates.TemplateResponse(request=request, name="profile.html", context={"user": user})

# security_basic = HTTPBasic()

#
# def get_user_by_name(
#         get_db_session: Annotated[Session, Depends(get_db)],
#         username: str
# ) -> Union[User, None]:
#     user = get_db_session.scalar(select(User).where(User.username == username))
#     if not user:
#         raise unauthenticated_exception()
#     return user
#
# def verify_password(user: User, password: str) -> bool:
#     hashed_password = sha256(password.encode()).hexdigest()
#     return secrets.compare_digest(user.password, hashed_password)
#
# def unauthenticated_exception() -> HTTPException:
#     return HTTPException(
#         status_code=401,
#         detail="Invalid username or password",
#         headers={
#             "WWW-Authenticate": "Basic",
#         }
#     )
#
# def get_auth_user_by_username(
#         get_db_session: Annotated[Session, Depends(get_db)],
#         username: str = Form(),
#         password: str = Form(),
#
# ) -> Union[User, None]:
#     # Проверяем пользователя
#     user: User = get_user_by_name(get_db_session, username)
#
#     if not user or not verify_password(user, password):
#         raise unauthenticated_exception()
#     return user
#
# @router.get("/")
# async def get_cookie_auth_template(
#         request: Request,
#         db: Annotated[Session,Depends(get_db)],
#         session_token: str | None = Cookie(alias="session_token")
#
# ):
#     if session_token:
#         auth_user: User = get_verify_session(session_token, db)
#         return templates.TemplateResponse(request=request, name="profile.html", context={"user": auth_user})
#     return templates.TemplateResponse(request=request, name="login.html")
#
#
# def save_session_to_db(
#         auth_user: User,
#         session_token: str,
#         db: Annotated[Session,Depends(get_db)]
# ):
#     new_session = UserSession(user_id=auth_user.id, session_token=session_token)
#     db.add(new_session)
#     db.commit()
#
#
#
# @router.post("/login-username")
# async def basic_auth_username(
#         auth_user: Annotated[User,Depends(get_auth_user_by_username)],
#         request: Request,
#         response: Response,
#         db: Annotated[Session,Depends(get_db)]
# ):
#     # Удаляем старые сессии пользователя из DB
#     try:
#         db.execute(delete(UserSession).where(UserSession.user_id == auth_user.id))
#         db.commit()
#     except AttributeError as e:
#         print(e)
#     session_token = generate_session_token()
#     save_session_to_db(auth_user, session_token, db)
#     response = templates.TemplateResponse(request=request, name="profile.html", context={"user": auth_user})
#     response.set_cookie(
#         key="session_token",
#         value=session_token,
#         httponly=True,  # Ограничиваем доступ к cookie только через HTTP (не через JS)
#         max_age=MAX_SESSIONS_LIFETIME,  # Время жизни куки
#         samesite="lax",  # Политика SameSite для защиты от CSRF
#         secure=False  # Установить True для HTTPS
#     )
#     return response
#
#
# def get_session_data(
#         db: Session = Depends(get_db),
#         session_token: str = Cookie(alias="session_token")
# ):
#
#     user_session = get_verify_session(session_token, db)
#     if not user_session:
#         raise HTTPException(status_code=401, detail="Invalid session")
#
#     return user_session.user
#
# @router.get("/profile")
# def get_profile(
#         user: User = Depends(get_session_data),
# ):
#     return {"username": user.username, "message": "Welcome to your profile"}

# # Logout
# @router.get("/logout")
# async def logout_user(
#         get_db_session: Annotated[Session, Depends(get_db)],
#         response: Response,
#         request: Request,
# ):
#
#     # session_token = request.cookies.get("session_token")
#     # if session_token:
#     #     get_db_session.execute(delete(UserSession).where(UserSession.session_token == session_token))
#     #     get_db_session.commit()
#     #
#     # response.delete_cookie("session_token")
#     return RedirectResponse(url='/')

#
# @router.post("/login-cookie")
# async def login_set_cookie(
#         auth_username: str = Depends(get_auth_user),
#
# ):
#     pass
#
# @router.get("/profile")
# def get_profile(
#         get_db_session: Annotated[Session, Depends(get_db)],
#         session_token: Union[str, None] = Cookie(None)
# ):
#
#     user = verify_session(get_db_session, session_token)
#     # Проверяем наличие токена
#     # if not session_token or session_token not in session_db:
#     #     raise HTTPException(status_code=401, detail="Not authenticated")
#
#     # Получаем пользователя по токену
#     # username = session_db[session_token]
#     return {"username": user.username, "message": "Welcome to your profile"}
#
#
#
# @router.get("/logout")
# def logout(
#         get_db_session: Annotated[Session, Depends(get_db)],
#         response: Response,
#         session_token: Union[str, None] = Cookie(None)
# ):
#
#     if session_token:
#         get_db_session.execute(delete(UserSession).where(UserSession.session_token == session_token))
#         get_db_session.commit()
#
#
#     # Удаляем токен из куки
#     response.delete_cookie("session_token")
#     return {"message": "Logged out successfully"}
#
#
@router.post("/register")
async def register_user(
        request: Request,
        get_db_session: Annotated[Session, Depends(get_db)],
        username: str = Form(...),  # Извлекаем username из данных формы
        password: str = Form(...),  # Извлекаем password из данных формы
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
