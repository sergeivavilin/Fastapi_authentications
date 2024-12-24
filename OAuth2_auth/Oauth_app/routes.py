from authlib.integrations.base_client import OAuthError

from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.templating import Jinja2Templates

from OAuth2_auth.Oauth_app.tools import oauth_exemple


router = APIRouter()

templates = Jinja2Templates(directory="OAuth2_auth/templates")

@router.get('/')
async def homepage(request: Request):
    user = request.session.get('user')
    if user:
        return RedirectResponse(url='/protected')
    # return HTMLResponse('<a href="/login">login</a>')
    return templates.TemplateResponse(request, "home.html")

@router.get("/login")
async def login(request: Request):
    user = request.session.get('user')
    if user:
        return RedirectResponse(url='/')
    # absolute url for callback
    #
    redirect_uri = request.url_for('auth')
    return await oauth_exemple.google.authorize_redirect(request, redirect_uri)

@router.get('/auth')
async def auth(request: Request):
    if 'user' in request.session:
        return RedirectResponse(url='/')

    try:
        token = await oauth_exemple.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>')

    user = token.get('userinfo')
    if user:
        request.session['user'] = dict(user)
    return RedirectResponse(url='/')

@router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')

@router.get('/protected')
async def protected(request: Request):
    user = request.session.get('user')
    if user:
        context_ = {'user': user}
        return templates.TemplateResponse(request, "protected.html", context=context_)
    return RedirectResponse(url='/')