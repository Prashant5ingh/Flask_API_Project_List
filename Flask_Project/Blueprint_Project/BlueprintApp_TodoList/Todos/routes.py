from flask import Flask,render_template, request,redirect,url_for,Blueprint

from BlueprintApp_TodoList.app import db
from BlueprintApp_TodoList.Todos.models import Todo  # Todo is table name. Todos here is dir name which contains models
#from BlueprintApp_TodoList.Todos.models import Todo

todos = Blueprint('Todos', __name__, template_folder='templates') # Todos is blueprint name and 'todos' is blueprint variable used for route decorators and registering blueprint in main app

@todos.route('/')
def index():
    todos = Todo.query.all()
    return render_template('todos/index.html', todos = todos) # render template is not using blueprint name instead given dir path for index.html

@todos.route('/create', methods=['GET','POST'])
def create():
    if request.method == 'GET':
        return render_template('todos/create.html')
    elif request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        done = True if 'done' in request.form.keys() else False

        description = description if description != "" else None

        todo = Todo(title = title, description = description, done = done )

        db.session.add(todo)
        db.session.commit()

        return redirect(url_for('Todos.index')) # In redirect we will use Blueprint name "Todos.index"