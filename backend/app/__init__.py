import json
import os
from pathlib import Path
from flask import Flask, jsonify
from flask_migrate import Migrate, init, upgrade, migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager




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

    app = Flask(__name__)
    app.config.from_object('app.config.Config')

   
    db.init_app(app)
    jwt.init_app(app)
    migrate_db.init_app(app, db)
    
    path = Path(os.getcwd(),'instance','app.db')
    if not path.exists():
        with app.app_context():
            import app.models
            db.create_all()

            db.session.commit()
            
            
    
    from app.api import assignment, auth, course, user, week,lecture
    app.register_blueprint(auth.auth_bp, url_prefix='/auth')
   

    setup_migrations(app)
    return app