from fastapi import FastAPI

from JWT_auth.JWT_app import routes


# Создаем экземпляр приложения
JWT_app = FastAPI()

# Добавляем роутеры в приложение
JWT_app.include_router(router=routes.router)
