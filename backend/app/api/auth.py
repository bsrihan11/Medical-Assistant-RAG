from flask import Blueprint
from flask.views import MethodView
from flask import request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token,\
    jwt_required, get_jwt_identity, set_access_cookies, \
        set_refresh_cookies, unset_jwt_cookies
from datetime import timedelta
from app.models import User
from app.utils import validate_email



auth_bp = Blueprint('auth', __name__)


class LoginAPI(MethodView):

    def post(self):
        """
        Handle user login by verifying the email and issuing JWT access and refresh tokens.

        Returns:
            JSON response with success message and sets access/refresh cookies if valid,
            or an error message if credentials are invalid.
        """
        
        data = request.get_json()

        if not validate_email(data.get('email','')):
            return jsonify(error='Invalid or missing email'),400
        
        
        user = User.query.filter_by(email = data.get('email')).first()
        if not user:
            return jsonify(error = 'Invalid user credentials'),401
            
            
        response = jsonify(message="Login successful")
        
        access_token = create_access_token(identity=str(user.id),expires_delta=timedelta(minutes=60))
        refresh_token = create_refresh_token(identity=str(user.id),expires_delta=timedelta(days=15))
        
        set_access_cookies(response,access_token,max_age=timedelta(minutes=55))
        set_refresh_cookies(response,refresh_token,max_age=timedelta(days=14))
        
        return response,200
      
    

class LogoutAPI(MethodView):
    
    @jwt_required(verify_type=False)
    def post(self):
        """
        Handle user logout by unsetting JWT cookies.

        Requires:
            A valid JWT (access or refresh) in the request cookies.

        Returns:
            JSON response confirming logout and clears authentication cookies.
        """

        response = jsonify(message="Logout successful")
        unset_jwt_cookies(response)
        
        return response,200
        
  

class RefreshAPI(MethodView):
    
    @jwt_required(refresh=True)
    def post(self):
        """
        Refresh the access token using a valid refresh token.

        Requires:
            A valid JWT refresh token in the request cookies.

        Returns:
            JSON response with a new access token set in cookies,
            or an error if the user is invalid.
        """
        
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify(error='Invalid request'),401

        response = jsonify(message="Access token refreshed")
        
            
        access_token = create_access_token(identity=str(user.id),expires_delta=timedelta(minutes=60))
        set_access_cookies(response,access_token,max_age=timedelta(minutes=55))
        
        return response,200

    


login_view = LoginAPI.as_view('login')
logout_view = LogoutAPI.as_view('logout')
refresh_view = RefreshAPI.as_view('refresh')

auth_bp.add_url_rule('/login', view_func=login_view, methods=['POST'])
auth_bp.add_url_rule('/logout', view_func=logout_view, methods=['POST'])
auth_bp.add_url_rule('/refresh',view_func=refresh_view,methods = ['POST'])