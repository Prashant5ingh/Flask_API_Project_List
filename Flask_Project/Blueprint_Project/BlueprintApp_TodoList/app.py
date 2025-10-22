from flask import Flask,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./blueprints.db'

    # Not going to use any secret key in this project
    
    db.init_app(app)

    # Import and register all blueprints
    from BlueprintApp_TodoList.Todos.routes import todos # 'todos' is blueprint variable in route.py
    app.register_blueprint(todos, url_prefix='/todos')  # url_prefix add a route before every routes created in route.py
    
    from BlueprintApp_TodoList.people.routes import people 
    app.register_blueprint(people, url_prefix='/people')  
   
    from BlueprintApp_TodoList.core.routes import core 
    app.register_blueprint(core, url_prefix='/')  



    migrate = Migrate(app, db)

    return app