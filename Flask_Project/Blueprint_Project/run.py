from BlueprintApp_TodoList.app import create_app,db
from flask_sqlalchemy import SQLAlchemy
flask_app = create_app()

if __name__ == '__main__':

    # Create database using create_all() method. It doesn't require to run flask migrate commands seperately.
    with flask_app.app_context():   
         db.create_all() # Create database tables for our data models
    flask_app.run(host='0.0.0.0', debug=True)


# Commands for Flask-Migrate (Database Migration)
    # flask db init --> only once for a project in that dir where main app.py present
    # flask db migrate -->Everytime whenever there is a change in schema or table. For Add a new class, add in new model and change in fields of a class.
    # flask db upgrade -->Everytime whenever there is a change in schema or table.
