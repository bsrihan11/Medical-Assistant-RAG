from flask import request, jsonify, Blueprint
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import  User
from app.utils import validate_user

user_bp = Blueprint('user', __name__)


class UserAPI(MethodView):
    
    @jwt_required()
    def get(self):
        """
        Retrieves the currently authenticated user's details.

        Requires a valid JWT token. Returns the user's information as JSON if found,
        otherwise returns a 404 error.
        """
        
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user:
            return jsonify(user.to_json()), 200
        
        return jsonify(error="User not found"), 404

    def post(self):
        """
        Registers a new user.

        Expects JSON payload with user data (e.g., email and name).
        Validates the input and creates a new user in the database.
        Returns the newly created user's information on success, or a 400 error on failure.
        """
        
        data = request.get_json()
        
        try:
            validate_user(data)
            
            new_user = User(email = data.get('email'), name = data.get('name'))
            
            db.session.add(new_user)
            db.session.commit()
            
                    
            return jsonify(message="User registered successfully", **new_user.to_json()), 201
        
        except Exception as e:
            return jsonify(error = str(e)), 400
    
    
    @jwt_required()
    def put(self):
        """
        Updates the currently authenticated user's data.

        Requires a valid JWT token and a JSON payload with updated user data.
        Validates the input and updates the user's details in the database.
        Returns the updated user information on success, or a 400/404 error if failed.
        """
        
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify(error="User not found"), 404
        
        data = request.get_json()
        try:
            
            validate_user(data,is_update=True)
            user.email = data.get('email')
            user.name = data.get('name')
            db.session.commit()
        
           
            
            return jsonify({"message": "User data updated successfully", **user.to_json()}),200
        
        except Exception as e:
            return jsonify(error = str(e)), 400
    

user_view = UserAPI.as_view('user_view')

user_bp.add_url_rule('/register', view_func=user_view, methods=['POST'])

user_bp.add_url_rule('/', view_func=user_view, methods=['GET'])

user_bp.add_url_rule('/update', view_func=user_view, methods=['PUT'])