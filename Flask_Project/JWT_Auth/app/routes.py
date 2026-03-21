from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, get_jwt
import bcrypt

from . import db
from .models import User
from .auth import generate_tokens

blacklist = set()

def register_routes(app):
    # --------------- REGISTER ----------------
    @app.route("/",methods=["GET"])
    def home():
        return {"message": "Welcome to the JWT Auth API!"}
    

    @app.route("/register", methods=["POST"])
    def register():
        data = request.json
        hashed = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt())
        user = User(username=data["username"], password=hashed)
        db.session.add(user)
        db.session.commit()
        return {"message": "User registered"}

    # --------------- LOGIN ----------------
    @app.route("/login", methods=["POST"])
    def login():
        data = request.json
        user = User.query.filter_by(username=data["username"]).first()
        if not user:
            return {"message": "User not found"}, 404
        if bcrypt.checkpw(data["password"].encode(), user.password):
            access, refresh = generate_tokens(user.id)
            return {"access_token": access, "refresh_token": refresh}
        return {"message": "Invalid password"}, 401

    # --------------- PROTECTED ROUTE ----------------
    @app.route("/profile")
    @jwt_required()
    def profile():
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        return {"id": user.id, "username": user.username}

    # --------------- REFRESH TOKEN ----------------
    @app.route("/refresh", methods=["POST"])
    @jwt_required(refresh=True)
    def refresh():
        user_id = get_jwt_identity()
        new_token = create_access_token(identity=user_id)
        return {"access_token": new_token}
    
    '''

❌ No — you should NOT use the refresh token as an access token.
✅ Refresh token is only used to generate a new access token.


    Login
  ↓
Access Token + Refresh Token
  ↓
Use Access Token for APIs
  ↓
Access Token expires
  ↓
Use Refresh Token
  ↓
Get NEW Access Token



Usage:
Frontend stores tokens
      ↓
API calls → Access Token
      ↓
Access expires
      ↓
Frontend calls /refresh
      ↓
New Access Token issued

    '''

    # --------------- LOGOUT ----------------
    @app.route("/logout", methods=["POST"])
    @jwt_required()
    def logout():
        jti = get_jwt()["jti"]
        blacklist.add(jti)
        return {"message": "Logged out"}