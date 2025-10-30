from flask import Flask, request, make_response, render_template, redirect, url_for, Response, send_from_directory, jsonify # type: ignore
from flask_sqlalchemy import SQLAlchemy 



db = SQLAlchemy()

def create_app():

    from models import Destination # Importing models inside the function to avoid circular imports.

    app = Flask(__name__) # created the application

    # restapi.db --> changed to 'restapi' and password '@' to '%40'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Primesql%409@localhost:3306/restapi'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./restapi.db'

    db.init_app(app)

    # Create the database tables (if they don't exist)
    # context manager to work with app context
    with app.app_context():
        db.create_all()


    @app.route('/', methods=['GET'])  # route decorator
    def index():
        return jsonify({"message": "Welcome to the Travel API!"}) 
   
    # Route to get all destinations from the database (GET method)
    @app.route('/destinations', methods=['GET'])    
    def get_destinations():
        destinations = Destination.query.all()
        return jsonify([destination.to_dict() for destination in destinations])
    
    # Route to get a specific destination by its ID (GET method)
    @app.route('/destination/<int:destination_id>', methods=['GET'])
    def get_destination(destination_id):
            destination = Destination.query.get(destination_id)
            if destination:
                return jsonify(destination.to_dict())
            else:
                return jsonify({"error": "Destination not found"}), 404
    
    # Route to add a new destination to the database (POST method)
    @app.route('/destinations', methods=['POST'])
    def add_destination():
         data = request.get_json()

         new_destination = Destination(destination = data["destination"],
                                       country = data['country'],
                                       rating = data['rating'])
         db.session.add(new_destination)
         db.session.commit()

         return jsonify(new_destination.to_dict()), 201  
    
    # Route to update an existing destination by its ID (PUT method)
    @app.route('/destination/<int:destination_id>', methods=['PUT'])
    def update_destination(destination_id):
         data = request.get_json()

         destination = Destination.query.get_or_404(destination_id) 
         
         destination.destination = data.get('destination', destination.destination)
         destination.country = data.get('country', destination.country)
         destination.rating = data.get('rating', destination.rating)
         
         db.session.commit()
         return jsonify(destination.to_dict()), 200
    
    # Route to delete a destination by its ID (DELETE method)
    @app.route('/destination/<int:destination_id>', methods=['DELETE'])
    def delete_destination(destination_id):
         destination = Destination.query.get(destination_id)

         if destination:
               db.session.delete(destination)
               db.session.commit()
               return jsonify({"message": "Destination deleted successfully"})
         else:
               return jsonify({"error": "Destination not found"}), 404


    return app