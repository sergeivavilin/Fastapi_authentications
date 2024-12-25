from hashlib import sha256

from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session

router = APIRouter(tags=["JWT auth"])


@router.get("/login")
async def login():
    return {"message": "Login"}


# Логин с JWT
@router.post("/jwt/token")
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
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/")
async def root():
    return {"message": "Hello JWT"}


