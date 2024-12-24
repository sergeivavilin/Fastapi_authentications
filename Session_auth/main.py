from fastapi import FastAPI
from fastapi.templating import Jinja2Templates

from Session_auth.session_app.routes import router


session_app = FastAPI()

session_app.include_router(router=router)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        app='main:session_app',
        host='localhost',
        port=8000,
        reload=True,
    )