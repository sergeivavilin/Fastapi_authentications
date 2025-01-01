from fastapi import FastAPI

from Session_auth.session_app import protected, routes

session_app = FastAPI()

session_app.include_router(router=routes.router)
session_app.include_router(router=protected.router)
