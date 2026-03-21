from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from .cache import init_cache

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    init_cache(app) # Initialize Redis cache after app creation

    from .routes import blog_bp
    app.register_blueprint(blog_bp)

    # with app.app_context():
    #     db.create_all()

    return app