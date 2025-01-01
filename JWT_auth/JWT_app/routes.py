from hashlib import sha256

from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import RedirectResponse

from JWT_auth.JWT_app.tools import create_access_token
from OAuth2_auth.Oauth_app.routes import templates
from Session_auth.session_app.database import get_db
from Session_auth.session_app.models import User

router = APIRouter(tags=["JWT auth"])


@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# Логин с JWT
@router.post("/login-jwt")
async def login_for_jwt(
        username: str = Form(),
        password: str = Form(),
        get_db_session: Session = Depends(get_db)
):
    hashed_password = sha256(password.encode()).hexdigest()
    user = get_db_session.query(User).filter(User.username == username).first()
    if not user or user.password != hashed_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Генерация токена
    access_token = create_access_token(
        payload={
            "sub": user.username,
        },
    )
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(key="access_token", value=access_token)

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/")
async def root():
    return {"message": "Hello JWT"}


