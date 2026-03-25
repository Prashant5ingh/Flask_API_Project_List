from flask import Flask, jsonify
from extensions import db, jwt
from auth import auth_bp
from users import user_bp
from models import User, TokenBlocklist
from dotenv import load_dotenv

# Load .env file BEFORE creating the app
load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config.from_prefixed_env()
    '''
app.config.from_prefixed_env() is a Flask method that automatically loads environment variables from your .env file.

How it works:

It looks for environment variables with the prefix FLASK_ and converts them to Flask config keys:

FLASK_SECRET_KEY → app.config['SECRET_KEY']
FLASK_SQLALCHEMY_DATABASE_URI → app.config['SQLALCHEMY_DATABASE_URI']
FLASK_DEBUG → app.config['DEBUG']
FLASK_SQLALCHEMY_ECHO → app.config['SQLALCHEMY_ECHO']

Is automatically loaded when app.config.from_prefixed_env() is called.

This is better than manually using os.getenv() because:

✅ Cleaner and more Pythonic
✅ Automatically handles the prefix stripping
✅ All Flask config variables in one method call
    '''

    # initialize exts
    db.init_app(app)
    jwt.init_app(app)

    # register bluepints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/users")

    # load user
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_headers, jwt_data):
        identity = jwt_data["sub"]

        return User.query.filter_by(username=identity).one_or_none()

    # additional claims

    @jwt.additional_claims_loader
    def make_additional_claims(identity):
        if identity == "janedoe123":
            return {"is_staff": True}
        return {"is_staff": False}

    # jwt error handlers

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        return jsonify({"message": "Token has expired", "error": "token_expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {"message": "Signature verification failed", "error": "invalid_token"}
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "message": "Request doesnt contain valid token",
                    "error": "authorization_header",
                }
            ),
            401,
        )
    
    @jwt.token_in_blocklist_loader
    def token_in_blocklist_callback(jwt_header,jwt_data):
        jti = jwt_data['jti']

        token = db.session.query(TokenBlocklist).filter(TokenBlocklist.jti == jti).scalar()

        return token is not None

    return app
