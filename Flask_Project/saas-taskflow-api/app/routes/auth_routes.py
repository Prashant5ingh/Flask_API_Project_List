from flask import Blueprint, request, jsonify
from app.services.auth_service import register_user, login_user
from app.utils.jwt import create_refresh_token, create_token, decode_token, jwt_required
from app.utils.cache import blacklist_token, is_token_blacklisted
from app import limiter

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new user."""
    # Get data
    data = request.json or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")
    
    # Validate input
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    
    # Register user
    user, error = register_user(email, password)
    
    if error:
        return jsonify({"error": error}), 400
    
    # Create token
    token = create_token(user.id)
    return jsonify({
        "message": "User registered successfully",
        "token": token,
        "user": {"id": user.id, "email": user.email}
    }), 201

@auth_bp.route("/login", methods=["POST"])
# @limiter.limit("5 per minute")  # 👈 prevent brute force attacks on this api endpoint. Overriding default rate limits
def login():
    """Login user and return token."""
    # Get data
    data = request.json or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")
    
    # Validate input
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    
    # Authenticate user
    user, error = login_user(email, password)
    
    if error:
        return jsonify({"error": error}), 401
    
    # Create token
    token = create_token(user.id)
    refresh_token = create_refresh_token(user.id)
    return jsonify({
        "message": "Login successful",
        "token": token,
        "refresh_token": refresh_token,
        "user": {"id": user.id, "email": user.email}
    }), 200

@auth_bp.route("/refresh", methods=["POST"])
@jwt_required
def refresh():
    """Refresh access token using refresh token."""
    data = request.json or {}
    refresh_token = data.get("refresh_token", "")
    
    if not refresh_token:
        return jsonify({"error": "Refresh token required"}), 400
    
    decoded = decode_token(refresh_token)
    
    if not decoded or decoded.get("type") != "refresh":
        return jsonify({"error": "Invalid refresh token"}), 401
    
    user_id = decoded.get("user_id") # fetching user_id from refresh token payload
    print(decoded.get("user_id"), user_id)
    new_token = create_token(user_id)
    
    return jsonify({
        "message": "Token refreshed",
        "token": new_token
    }), 200

# can add logout route later if we implement token blacklisting or use short-lived tokens with refresh tokens. For now, we can just rely on token expiration for security.
@auth_bp.route("/logout", methods=["POST"])
@jwt_required
def logout():
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.split(" ")[-1]
    data = decode_token(token)
    if not data:
        return jsonify({"error": "Invalid token"}), 401
    
    jti = data.get("jti")
    blacklist_token(jti)
    return jsonify({"message": "Logout successful, token revoked"}), 200
'''
Purpose: Handle user registration and login, returning JWT tokens for authentication.

Key improvements:
✅ Handles errors from services
✅ Validates input before use
✅ Proper HTTP status codes (201 for created, 401 for unauthorized)
✅ Both endpoints return token
✅ Uses jsonify() for consistency
✅ Safe .get() instead of direct dictionary access
✅ Returns user info alongside token
'''