from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()


''' 
When is init_app() NOT needed?
Only if you pass the app directly when creating the extension:
app = Flask(__name__)
db = SQLAlchemy(app)      # ✅ Direct initialization, no init_app() needed
jwt = JWTManager(app)     # ✅ Direct initialization, no init_app() needed
'''
def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
    app.config["JWT_SECRET_KEY"] = "super-secret"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600
    
    db.init_app(app)
    jwt.init_app(app)
    
    # Register token revocation checker
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        from . import routes
        jti = jwt_payload["jti"]
        return jti in routes.blacklist
    '''
    Token Revocation: Depends on your needs
Revocation is for blacklisting tokens (logout scenario).

Do you need it if:

✅ Users can logout and token should become invalid
✅ You want to revoke specific user sessions
✅ User password changes (old tokens should be invalid)
Don't need it if:

Tokens are short-lived (24 hours in your code) — user just waits for expiration
No logout endpoint needed
    '''
    
    # Import routes AFTER initializing extensions
    from . import routes
    routes.register_routes(app)
    
    return app