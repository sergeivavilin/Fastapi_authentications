from fastapi import FastAPI

from JWT_auth.JWT_app import routes


JWT_app = FastAPI()
JWT_app.include_router(router=routes.router)


if __name__ == '__main__':
    import uvicorn


    uvicorn.run(
        app="main:JWT_app",
        host="127.0.0.1",
        port=8002,
        reload=True
    )