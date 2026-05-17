from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
from app import db
import re

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Check if password meets minimum requirements."""
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    return True, None

def register_user(email, password):
    """Register a new user."""
    # Validate inputs
    if not email or not password:
        return None, "Email and password required"
    
    if not validate_email(email):
        return None, "Invalid email format"
    
    is_valid, msg = validate_password(password)
    if not is_valid:
        return None, msg
    
    # Check if email already exists
    if User.query.filter_by(email=email).first():
        return None, "Email already registered"
    
    try:
        user = User(email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        return user, None
    except Exception as e:
        db.session.rollback()
        return None, f"Registration failed: {str(e)}"

def login_user(email, password):
    """Authenticate user."""
    if not email or not password:
        return None, "Email and password required"
    
    user = User.query.filter_by(email=email).first() # Query the database for a user with the provided email. If no user is found, it returns None. If a user is found, it proceeds to check the password.
    
    if not user:
        return None, "Invalid email or password"
    
    if not check_password_hash(user.password_hash, password):
        return None, "Invalid email or password"
    
    return user, None



'''
Issues Resolved:
No duplicate email check — register_user() will crash if email exists
No input validation — doesn't check email format or password strength
No error handling — doesn't return error messages
No logging — hard to debug issues
'''