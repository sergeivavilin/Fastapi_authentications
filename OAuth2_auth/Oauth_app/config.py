import os

from dotenv import load_dotenv

load_dotenv()

# Данные для авторизации приложения к авторизации через Google
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
