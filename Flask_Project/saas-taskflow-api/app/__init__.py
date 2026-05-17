from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from .utils.cache import init_cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded

# from flask_jwt_extended import JWTManager # We are not using Flask-JWT-Extended in this project, so we can remove this import and the related code.

db = SQLAlchemy()
# jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address, default_limits=Config.DEFAULT_RATELIMIT, storage_uri=Config.REDIS_URL) # Using Redis for rate limit storage, can also use in-memory for development but Redis is better for production.
'''
Custom key function to rate limit based on user ID if authenticated, otherwise fall back to IP address. This allows us to have different rate limits for authenticated users vs unauthenticated users.
For example, we can allow more requests for authenticated users while still protecting against abuse from unauthenticated requests.

from flask import request
from app.utils.jwt import decode_token

def get_user_key():
    """Get rate limit key based on user ID (if authenticated) or IP address"""
    # Try to get user ID from JWT token in Authorization header
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.split(" ")[-1] if auth_header else None
    
    if token:
        payload = decode_token(token)
        if payload and "user_id" in payload:
            return f"user_{payload['user_id']}"  # Rate limit per authenticated user
    
    # Fall back to IP address for unauthenticated requests
    return get_remote_address()

limiter = Limiter(key_func=get_user_key, default_limits=Config.DEFAULT_RATELIMIT, storage_uri=Config.REDIS_URL)

Result:
✅ Authenticated users: Each user gets their own rate limit (5 per minute per user)
✅ Unauthenticated users: Rate limited by IP address
✅ Different users from same IP: Each gets their own 5 per minute limit
'''

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    init_cache(app) # Initialize Redis cache after app creation
    limiter.init_app(app)
    # jwt.init_app(app)

    # ✅ Add this error handler for rate limit exceeded
    @app.errorhandler(RateLimitExceeded)
    def ratelimit_handler(e):
        return jsonify({
            "error": "API Rate Limit Exceeded",
            "message": str(e.description)
        }), 429

    # Import all models so SQLAlchemy knows about them before creating tables
    from app.models.user import User
    from app.models.organization import Organization
    from app.models.project import Project
    from app.models.task import Task
    from app.models.assignment import TaskAssignment
    from app.models.comment import Comment
    from app.models.organization_member import OrganizationMember


    # Register token revocation checker
    # @jwt.token_in_blocklist_loader
    # def check_if_token_revoked(jwt_header, jwt_payload):
    #     from . import routes
    #     jti = jwt_payload["jti"]
    #     return jti in routes.blacklist

    # Register routes
    from app.routes.auth_routes import auth_bp

    from .routes.project_routes import project_bp # This type of import is possible because of __init__.py in routes folder which allows us to import from routes as a package. 
    #from app.routes.project_routes import project_bp

    from app.routes.task_routes import task_bp
    from app.routes.organization_routes import organization_bp
    from app.routes.comment_routes import comments_bp
    from app.routes.org_member_routes import org_bp
    from app.routes.assignedTask_routes import assignments_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(project_bp, url_prefix="/api/projects")
    app.register_blueprint(task_bp, url_prefix="/api/tasks") 
    app.register_blueprint(organization_bp, url_prefix="/api/organizations")
    app.register_blueprint(comments_bp, url_prefix="/api") # Register comments blueprint with /api prefix
    app.register_blueprint(org_bp, url_prefix="/api") # Register org member blueprint with /api prefix
    app.register_blueprint(assignments_bp, url_prefix="/api")

    return app

'''
But using /api is good practice because:

✅ Clear separation between API endpoints and web pages
✅ Easier API versioning later (/api/v1/, /api/v2/)
✅ Industry standard
✅ Makes routing clear to frontend developers

Without /api:           With /api:
POST /auth/login        POST /api/auth/login
GET /tasks              GET /api/tasks
DELETE /tasks/1         DELETE /api/tasks/1
Recommendation: Use /api for clarity, especially if you might add non-API routes later (like web pages, webhooks, etc.).
'''

'''
1. Using our custom JWT implementation in app/utils/jwt.py instead of Flask-JWT-Extended for more control and simplicity.

2. Token Revocation: Depends on your needs (logout route, token revocation and token blacklisting can be added later if needed)
Revocation is for blacklisting tokens (logout scenario).

Do you need it if:
✅ Users can logout and token should become invalid
✅ You want to revoke specific user sessions
✅ User password changes (old tokens should be invalid)

Don't need it if:
Tokens are short-lived (24 hours in your code) — user just waits for expiration
No logout endpoint needed

Skip token revocation for now if tokens are short-lived (24 hours)
Add logout + revocation later if users request it

3. Rate Limiting is also a good idea to prevent abuse, but can be added later as well. For now, focus on core functionality and add these features based on user feedback and needs.

4. Token Refreshing can also be added later if you want to implement refresh tokens for better security and user experience, but it's not strictly necessary for a basic implementation. You can rely on short-lived access tokens and have users log in again after expiration for simplicity.

'''