from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from OAuth2_auth.Oauth_app.routes import router


# Создаем приложение для OAauth2 аутентификации
oauth2_app = FastAPI()

# Добавляем встроенный мидлварь для обработки запросов и ответов пользователя
# Хранение, создание и получение токенов происходит автоматически
oauth2_app.add_middleware(SessionMiddleware, secret_key="very-secret-key")

# Добавляем роутер для OAuth2 авторизации
oauth2_app.include_router(router=router)
