from authlib.integrations.starlette_client import OAuth

from OAuth2_auth.Oauth_app.config import CLIENT_ID, CLIENT_SECRET

oauth_exemple = OAuth()
oauth_exemple.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    client_kwargs={
        'scope': 'openid email profile'
    }
)

