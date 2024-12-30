from fastapi import FastAPI

from Session_auth.session_app import cookie_auth, protected, session_router, routes

session_app = FastAPI()

session_app.include_router(router=routes.router)
session_app.include_router(router=protected.router)
# session_app.include_router(router=session_router.router)
# session_app.include_router(router=cookie_auth.router)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        app='main:session_app',
        reload=True,
    )