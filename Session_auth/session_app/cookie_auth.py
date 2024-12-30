from hashlib import sha256
from typing import Annotated

from fastapi import FastAPI, APIRouter, Response, Cookie, Form, HTTPException

from datetime import datetime

from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from starlette.requests import Request
from starlette.responses import RedirectResponse

from Session_auth.session_app.database import get_db
from Session_auth.session_app.models import UserSession, User
from Session_auth.session_app.tools import templates, generate_session_token

router = APIRouter(tags=["Cookie-auth"])


def get_verified_user(
        session_token: str = Cookie(alias="session_token"),
        db: Session = Depends(get_db)
):
    if session_token:
        user = db.scalar(select(UserSession).where(UserSession.session_token == session_token))
        if user is not None:
            return user
    return None



@router.get("/")
async def home_page(request: Request):
    return templates.TemplateResponse(request=request, name="home.html")

@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse(request=request, name="register.html")


def get_auth_user_by_username(
        db: Session = Depends(get_db),
        username: str = Form(),
        password: str = Form(),
):
    hashed_password = sha256(password.encode()).hexdigest()
    user = db.scalar(select(User).where(User.username == username))
    if user and user.password == hashed_password:
        return user
    raise HTTPException(status_code=401, detail="Incorrect username or password")

@router.post("/login-username")
async def login_username(
        auth_user: Annotated[User,Depends(get_auth_user_by_username)],
        request: Request,
        response: Response,
):
    session_token = generate_session_token()
    response = RedirectResponse(url="/profile", status_code=302)
    response.set_cookie(key="session_token", value=session_token, httponly=True)
    return response



@router.get("/profile")
async def profile_page(
        request: Request,

        # verified_user: Annotated[User, Depends(get_verified_user)]
):
    token = request.get("session_token")
    if token:
        verified_user = get_verified_user(session_token=token)

        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={"user": verified_user}
        )
    raise HTTPException(
        status_code=401,
        detail="You are not logged in"
    )

