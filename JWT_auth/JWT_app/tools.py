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


# Настройки для шифрования токена
JWT_ERROR = jwt.PyJWTError
JWT_SECRET_KEY = "JWT_SECRET_KEY"
JWT_ALGORITHM = "HS256"
MAX_JWT_ACCESS_LIFETIME = 5

templates = Jinja2Templates(directory=f"JWT_auth{os.sep}templates")

def create_access_token(
        payload: dict,
        key: str = JWT_SECRET_KEY,
        algorithm: str = JWT_ALGORITHM,
        exp_timedelta: datetime.timedelta = datetime.timedelta(minutes=MAX_JWT_ACCESS_LIFETIME),
):
    """
    Функция хелпер для создания токена доступа
    :param payload: Полезные данные для передачи вместе с токеном
    :param key:  Ключ для шифрования токена
    :param algorithm:   Алгоритм шифрования токена
    :param exp_timedelta:  Время жизни токена
    :return: Зашифрованный токен
    """
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
    """
    Функция хелпер для дешифровки токена
    :param token:  Токен
    :param key:  Ключ для шифрования токена
    :return:  Дешифрованный токен
    """
    return jwt.decode(token, key, algorithms=["HS256"], leeway=20)


def hash_password(password: str) -> str:
    """
    Функция хелпер для хэширования пароля
    :param password:  Пароль для хэширования
    :return: Хэш пароля
    """
    return sha256(password.encode()).hexdigest()


def exist_user(
        get_db_session: Annotated[Session, Depends(get_db)],
        username: str = Form(),
):
    """
    Функция хелпер для проверки существования пользователя
    :param get_db_session: ORM-Сессия для работы с БД
    :param username:  Имя пользователя
    :return: bool - True если пользователь существует, False если нет
    """
    user = get_db_session.scalar(select(User).filter(User.username == username))
    if user:
        return True
    return False


def validate_user(
        get_db_session: Annotated[Session, Depends(get_db)],
        username: str = Form(),
        password: str = Form(),
):
    """
    Функция хелпер для валидации пользователя
    :param get_db_session: ORM-Сессия для работы с БД
    :param username:  Имя пользователя
    :param password:  Пароль пользователя
    :return:  Пользователь если он существует, None если нет
    """
    hashed_password = hash_password(password)
    user = get_db_session.scalar(select(User).filter(User.username == username))

    if not user or user.password != hashed_password:
        return None

    return user


def verify_access_token(access_jwt_token) -> dict:
    """
    Функция хелпер для проверки токена и возврата данных юзера
    :param access_jwt_token:  Токен
    :return: dict - Данные юзера из токена
    """
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
    """
    Функция хелпер для получения данных юзера из токена
    :param access_jwt_token_:  Токен
    :return: dict - Данные юзера из токена или ошибка 401 если токен не найден
    """
    if not access_jwt_token_:
        raise HTTPException(status_code=401, detail="Token not found")
    return verify_access_token(access_jwt_token_)

def get_all_users_from_db(
        get_db_session: Session = Depends(get_db)
):
    """
    Функция хелпер для получения всех пользователей из БД
    :param get_db_session: ORM-Сессия для работы с БД
    :return:  Список пользователей
    """
    return get_db_session.scalars(select(User)).all()


def create_user(
        get_db_session: Annotated[Session, Depends(get_db)],
        username: str,
        password: str,
):
    """
    Функция хелпер для создания пользователя
    :param get_db_session: ORM-Сессия для работы с БД
    :param username:  Имя пользователя
    :param password:  Пароль пользователя
    :return:  True если пользователь создан, False если нет
    """
    hashed_password = hash_password(password)
    user = User(username=username, password=hashed_password)
    try:
        get_db_session.add(user)
        get_db_session.commit()
    except Exception as e:
        print(e)
        return False
    return True