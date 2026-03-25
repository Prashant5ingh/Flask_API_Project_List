from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from .utils.cache import init_cache
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    init_cache(app) # Initialize Redis cache after app creation
    jwt.init_app(app)

    # Register token revocation checker
    # @jwt.token_in_blocklist_loader
    # def check_if_token_revoked(jwt_header, jwt_payload):
    #     from . import routes
    #     jti = jwt_payload["jti"]
    #     return jti in routes.blacklist

    # from .routes import blog_bp
    # app.register_blueprint(blog_bp) 

    # with app.app_context():
    #     db.create_all()

    return app