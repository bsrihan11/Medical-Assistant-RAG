import re
from app.models import User


def validate_length(string,min=1,max=None):    
    if min<=len(string)<=max:
        return True

    return False


def validate_email(email):
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    
    if not re.match(email_pattern, email):
        return False

    return True


def validate_user(user, is_update=False):
    
    assert user['email'] and isinstance(user['email'], str) and validate_length(user['email'], max=100) and \
        validate_email(user['email']), "Invalid or Missing Email"
    
    if not is_update:
        assert not User.query.filter_by(email=user['email']).first(), "Email already exists"
    
    assert user['name'] and isinstance(user['name'], str) and \
        validate_length(user['name'], max=100), "Invalid or Missing Name"
    