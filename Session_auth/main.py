from fastapi import FastAPI

from Session_auth.session_app import routes, protected


session_app = FastAPI()

session_app.include_router(router=routes.router)
session_app.include_router(router=protected.router)


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        app='main:session_app',
        reload=True,
    )