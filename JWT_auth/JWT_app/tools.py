import datetime

import jwt


JWT_SECRET_KEY = "JWT_SECRET_KEY"


def create_access_token(
        payload,
        key=JWT_SECRET_KEY,
        algorithm='HS256',
        exp_timedelta=datetime.timedelta(minutes=15)
):
    token = jwt.encode(
        payload=payload,
        key=key,
        algorithm=algorithm,
        expires_time=exp_timedelta

    )
    return token


def decode_token(token, key):
    return jwt.decode(token, key, algorithms=["RS256"])


def hash_password(password):
    pass