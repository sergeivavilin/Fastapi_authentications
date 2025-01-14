from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from OAuth2_auth.Oauth_app.routes import router

oauth2_app = FastAPI()
oauth2_app.add_middleware(SessionMiddleware, secret_key="very-secret-key")

oauth2_app.include_router(router=router)

