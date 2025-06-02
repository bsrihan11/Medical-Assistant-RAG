import os
from dotenv import load_dotenv

load_dotenv()
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_COOKIE_SECURE=False
    JWT_TOKEN_LOCATION=["cookies"]
    JWT_SECRET_KEY= os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES=15
    JWT_REFRESH_TOKEN_EXPIRES=12