import uuid

import jwt
from datetime import datetime, timezone, timedelta
from app.utils.cache import blacklist_token, is_token_blacklisted
from flask import request, jsonify, current_app
from functools import wraps

'''
This file implements a complete JWT authentication system — token creation on login, 
token validation on protected endpoints, and automatic user identification.
'''


def create_token(user_id):  # Generate a JWT token with user ID and expiration time
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24), #
        # "iat": datetime.now(), issued at time, can be useful for token management and debugging
        "jti": str(uuid.uuid4())  # unique token ID
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm="HS256")

def create_refresh_token(user_id): # Generate a refresh token with a longer expiration time, used to obtain new access tokens without re-authenticating the user.
    payload = {
        "user_id": user_id,
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=7)
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm="HS256")

def decode_token(token): # Decode the JWT token and return the payload if valid, otherwise return None
    try:
        return jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def jwt_required(f): # Decorator to protect routes that require authentication. It checks for the token in the Authorization header, decodes it, and attaches the user ID to the request context.
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.split(" ")[-1] if auth_header else None
        
        if not token:
            return jsonify({"error": "Missing token"}), 401
        
        data = decode_token(token)
        if not data:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Check blacklist
        if is_token_blacklisted(data["jti"]):
            return jsonify({"error": "Token has been revoked due to logout"}), 401
        
        request.user_id = data["user_id"]
        return f(*args, **kwargs)
    return wrapper

'''
Issues Resolved:
Hardcoded secret — You have SECRET_KEY and JWT_SECRET_KEY defined in config.py. Use that instead:

Bare except clause — Catches all exceptions. Be more specific:

Deprecated datetime.utcnow() — If using Python 3.12+, use datetime.now(timezone.utc) instead

Bearer token format — Standard JWT format is "Bearer <token>", but your code just looks for the raw token. Consider:

Missing error response format — Consider using Flask's jsonify() for consistency
'''