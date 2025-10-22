from app import create_app

flask_app = create_app()

if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', debug=True)
    # flask db init --> only once for a project
    
    # flask db migrate -->Everytime whenever there is a change in schema or table. For Add a new class, add in new model and change in fields of a class.
    # flask db upgrade -->Everytime whenever there is a change in schema or table.
