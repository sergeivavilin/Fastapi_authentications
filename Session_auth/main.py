from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

session_app = FastAPI()

templates = Jinja2Templates(directory="Session_auth/templates")

@session_app.get("/")
async def main_index(request: Request):

    return templates.TemplateResponse(request, "home.html")
    #     name="home.html",
    #     context={"request": request}
    # )