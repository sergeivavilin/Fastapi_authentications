# Указываем параметры для BD
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URL = f"sqlite:///{BASE_DIR}{os.sep}auth.db"
