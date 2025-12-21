from flask import Flask, jsonify, request, render_template, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests

from dotenv import load_dotenv
load_dotenv()  # loads .env from project root

import os

app = Flask(__name__)

# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:mysecretpassword@localhost:5433/todolist_db"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todolist.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# Data Class ~ Row of data in table
class Todo(db.Model):
    """A Model for an Item in the Todo List

    Args:
        db (_type_): database model

    Returns:
        __repr__: string rep.
    """
    id = db.Column(db.String, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    # completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return {
                "id": self.id,
                "content": self.content,
                "date_created": self.date_created
            }
    

with app.app_context(): # Create the database and the db table
    db.create_all()

    

# Not needed as we are using proxy in vite config (React Js) for local development
CORS(
    app,
    resources={r"/*": {"origins": ["http://localhost:5173","http://localhost:5174","http://localhost:3000", "https://frontend-nine-ebon-34.vercel.app"], "methods": ["GET", "POST","DELETE"]}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"]
)

@app.route('/tasklist', methods=['GET'])
def get_tasks():
    tasks = Todo.query.order_by(Todo.date_created).all()
    # print("tasks",tasks)
    
    return jsonify([task.__repr__() for task in tasks])
    # return jsonify([{'id': "task.id", 'content': "new task", 'date_created': "task.date_created"},{'id': "task.id", 'content': "hardcoded task", 'date_created': "task.date_created"}])
    

@app.route('/addtask', methods=['POST'])
def add_task():
    content = request.json.get('content')
    id = request.json.get('id')
    if not content and id:
        return jsonify({'error': 'Content or id is required'}), 400
    new_task = Todo(content=content,
                    id=id)
    db.session.add(new_task)
    db.session.commit()
    return jsonify({'message': 'Task added successfully'}), 201

@app.route('/deletetask/<string:id>', methods=['DELETE'])
def delete_task(id):
          print(id, type(id))
          task_to_delete = Todo.query.get_or_404(id)
          try:
            db.session.delete(task_to_delete)
            db.session.commit()
            return jsonify({"message": "Task deleted successfully"})
          except Exception as e:
            return jsonify({"error": "Failed to delete task, Reason: " + str(e)}), 500           


@app.route('/api/github')
def github_api():
        # Third‑party HTTP client library to make a GET request to an external API. Used to make outgoing HTTP calls from your Python code to other services.
        # Example: call an external API, download files, etc.
        resp = requests.get("https://api.github.com/users/Prashant5ingh") # Github API request. --> fetch data of all users in a list
        # resp = requests.get("https://api.github.com/users/octocat") # Github API request.
        print("Response status code: ", resp.status_code)
        print("Response type: ", type(resp))
        if resp.ok:
             data = resp.json()
            #  print(data) # --> print user data
            #  print(data.get("login")) # --> print user login name data
            #  print(data["name"]) # --> print user site admin boolean data

            # return jsonify(data[:5]) # top 5 result for resp = requests.get("https://api.github.com/users")
             return jsonify(data)

            #  print(data.get("login")) --> data fetching for specific user
            #  print(data["name"])
        return jsonify({'message':'Failed to fetch data from Github API'}), resp.status_code
     
if __name__ == '__main__':
    PORT = int(os.environ.get("PORT",5500))
    app.run(debug=True, host='0.0.0.0', port=PORT)
    # use host '0.0.0.0' for production/containers, 'localhost' for local dev.