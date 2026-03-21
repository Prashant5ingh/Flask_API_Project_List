from flask_jwt_extended import create_access_token, create_refresh_token

from .models import User
import bcrypt

def generate_tokens(user_id):

    access = create_access_token(identity=user_id)
    refresh = create_refresh_token(identity=user_id)
    return access, refresh
def hash_password(password):
    """Hash a password"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verify_password(password, hashed):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode(), hashed)

def get_user_by_username(username):
    """Get user from database by username"""
    return User.query.filter_by(username=username).first()