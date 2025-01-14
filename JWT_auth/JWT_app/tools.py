import datetime
import os
from hashlib import sha256
from typing import Optional, Annotated

import jwt
from fastapi import Depends, HTTPException, Form
from fastapi.params import Cookie
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.templating import Jinja2Templates

from Session_auth.session_app.database import get_db
from Session_auth.session_app.models import User

JWT_ERROR = jwt.PyJWTError
JWT_SECRET_KEY = "JWT_SECRET_KEY"
MAX_JWT_ACCESS_LIFETIME = 5

templates = Jinja2Templates(directory=f"JWT_auth{os.sep}templates")

def create_access_token(
        payload: dict,
        key: str = JWT_SECRET_KEY,
        algorithm: str = "HS256",
        exp_timedelta: datetime.timedelta = datetime.timedelta(minutes=MAX_JWT_ACCESS_LIFETIME),
):
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    expire = now + exp_timedelta
    payload.update(
        exp=expire,
        iat=now,
    )

    token = jwt.encode(
        payload=payload,
        key=key,
        algorithm=algorithm,
    )
    return token


def decode_token(
        token,
        key: str = JWT_SECRET_KEY
):
    return jwt.decode(token, key, algorithms=["HS256"], leeway=20)


def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()


def exist_user(
        get_db_session: Annotated[Session, Depends(get_db)],
        username: str = Form(),
):
    user = get_db_session.scalar(select(User).filter(User.username == username))
    if user:
        return True
    return False


def validate_user(
        get_db_session: Annotated[Session, Depends(get_db)],
        username: str = Form(),
        password: str = Form(),
):
    hashed_password = hash_password(password)
    user = get_db_session.scalar(select(User).filter(User.username == username))

    if not user or user.password != hashed_password:
        return None

    return user


def verify_access_token(access_jwt_token) -> dict:
    try:
        payload = decode_token(access_jwt_token)

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWT_ERROR as error:
        raise HTTPException(status_code=401, detail=f"{error}")

    return payload

def get_payload(
        access_jwt_token_: Optional[str] = Cookie(alias="access_jwt_token"),
):
    if not access_jwt_token_:
        raise HTTPException(status_code=401, detail="Token not found")
    return verify_access_token(access_jwt_token_)

def get_all_users_from_db(
        get_db_session: Session = Depends(get_db)
):
    return get_db_session.scalars(select(User)).all()


def create_user(
        get_db_session: Annotated[Session, Depends(get_db)],
        username: str,
        password: str,
):
    hashed_password = hash_password(password)
    user = User(username=username, password=hashed_password)
    try:
        get_db_session.add(user)
        get_db_session.commit()
    except Exception as e:
        print(e)
    return True