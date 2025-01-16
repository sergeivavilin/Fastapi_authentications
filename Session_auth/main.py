from fastapi import FastAPI

from Session_auth.session_app import protected, routes

# Создаем экземпляр приложения
session_app = FastAPI()

# Добавляем роутеры в приложение
session_app.include_router(router=routes.router)
session_app.include_router(router=protected.router)
