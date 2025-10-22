from flask import Flask,render_template, request,redirect,url_for,Blueprint

from BlueprintApp_TodoList.app import db
from BlueprintApp_TodoList.people.models import Person  # Todo is table name
#from BlueprintApp_TodoList.Todos.models import Todo

people = Blueprint('People', __name__, template_folder='templates') # Todos is blueprint name and 'todos' is blueprint variable used for route decorators and registering blueprint in main app

@people.route('/')
def index():
    people = Person.query.all()
    return render_template('people/index.html', people = people) # render template is not using blueprint name instead given dir path for index.html

@people.route('/create', methods=['GET','POST'])
def create():
    if request.method == 'GET':
        return render_template('people/create.html')
    elif request.method == 'POST':
        name = request.form.get('name')
        age = int(request.form.get('age'))
        job = request.form.get('job')

        job = job if job != "" else None

        person = Person(name = name, age = age, job = job )

        db.session.add(person)
        db.session.commit()

        return redirect(url_for('People.index')) # In redirect we will use Blueprint name "Todos.index"