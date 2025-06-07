import os
from dotenv import load_dotenv

load_dotenv()
class AppConfig:
    """Base configuration for the Flask app."""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///rag.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_COOKIE_SECURE=False
    JWT_TOKEN_LOCATION=["cookies"]
    JWT_SECRET_KEY= os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES=15
    JWT_REFRESH_TOKEN_EXPIRES=12
    
    
class RagConfig:
    """Configuration for RAG """ 
    MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY')
    MISTRAL_API_URL = os.environ.get('HF_TOKEN')