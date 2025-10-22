from flask import Flask,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt


db = SQLAlchemy()

# tO avoid the circular imports. Imports the file when this function is called
def create_app():
   # app = Flask(__name__, template_folder='templates') # Templates folder for user details in database
    
    app = Flask(__name__, template_folder='Auth_Templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./test.db'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:5432/your_db_name' or to use any sql.
    
    app.secret_key="newsessiondb" # Needed for userAuth concept

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    from models import UserAuth
    @login_manager.user_loader # login Manager loads the user
    def load_user(uid):
        # loads user based on uid
        return UserAuth.query.get(uid)
    
    @login_manager.unauthorized_handler
    def unauthorize_callback(): # Handling the unauthorize page or message as custom msg string or redirect
        # return redirect(url_for('authIndex'))
        return 'Not authorized to access'

    bcrypt = Bcrypt(app) # This line initializes the Bcrypt extension with your Flask app, allowing you to use it for password hashing and verification.


    # imports
    from routes import register_routes, authRoutes
    # register_routes(app,db)
    authRoutes(app,db,bcrypt)

    migrate = Migrate(app, db)

    return app