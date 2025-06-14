import json
import os
from pathlib import Path
from flask import Flask, jsonify
from flask_migrate import Migrate, init, upgrade, migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS


db = SQLAlchemy()
migrate_db = Migrate()
jwt = JWTManager()


@jwt.unauthorized_loader
def custom_unauthorized_response(error):
    return jsonify(error = "Authorization token is missing or invalid"), 401


@jwt.invalid_token_loader
def custom_invalid_token_response(error):
    return jsonify(error = "The token provided is expired or malformed"), 401



def setup_migrations(app):
    """Initialize and run migrations automatically."""
    
    with app.app_context():
        if not os.path.exists("migrations"):
            try:
                print("Initializing migrations folder...")
                init()
            except Exception as e:
                print(f"Migration init failed: {e}")

        print("Generating migration script...")
        migrate()
        print("Applying migrations...")
        upgrade()


def create_app():
    """Initialize the Flask App."""

    flask_app = Flask(__name__)
    flask_app.config.from_object('app.config.AppConfig')

   
    db.init_app(flask_app)
    jwt.init_app(flask_app)
    migrate_db.init_app(flask_app, db)
    
    path = Path(os.getcwd(),'instance','rag.db')
    if not path.exists():
        with flask_app.app_context():
            import app.models
            db.create_all()

            db.session.commit()
            
    CORS(flask_app, origins=["http://localhost:8080"], supports_credentials=True)
        
    from app.api import  auth, chats, user
    flask_app.register_blueprint(auth.auth_bp, url_prefix='/auth')
    flask_app.register_blueprint(chats.chats_bp,url_prefix='/chat')
    flask_app.register_blueprint(user.user_bp, url_prefix='/user')

    setup_migrations(flask_app)
    return flask_app



    