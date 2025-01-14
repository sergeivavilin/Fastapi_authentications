from fastapi import FastAPI

from JWT_auth.JWT_app import routes

JWT_app = FastAPI()
JWT_app.include_router(router=routes.router)
