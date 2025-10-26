from flask import Flask,render_template, request,redirect,url_for,Blueprint

from BlueprintApp_TodoList.app import db
from BlueprintApp_TodoList.Todos.models import Todo  # Todo is table name. Todos here is dir name which contains models
#from BlueprintApp_TodoList.Todos.models import Todo

todos = Blueprint('Todos', __name__, template_folder='templates') # Todos is blueprint name and 'todos' is blueprint variable used for route decorators and registering blueprint in main app

todosArr = []

@todos.route('/')
def index():
    # todosArr.clear()
    todos = Todo.query.all()
    # for todo in todos:
    #     todosArr.append({'title': todo.title,'description': todo.description, 'done': todo.done})
    # print(todosArr)

    return render_template('todos/index.html', todos = todos) # render template is not using blueprint name instead given dir path for index.html
    # return render_template('todos/index.html', todos = todos) # render template is not using blueprint name instead given dir path for index.html

@todos.route('/create', methods=['GET','POST'])
def create():
    if request.method == 'GET':
        return render_template('todos/create.html')
    elif request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        done = True if 'done' in request.form.keys() else False

        description = description if description != "" else None

        todosArr.append({'title': title,'description': description, 'done': done})

        todo = Todo(title = title, description = description, done = done )
        print(todo)

        db.session.add(todo)
        db.session.commit()

        return redirect(url_for('Todos.index')) # In redirect we will use Blueprint name "Todos.index"
    
@todos.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit(index):
    # todo = todosArr[index]
    todo = Todo.query.get(index)  # or get_or_404(id)
    if request.method == "POST":
        # todo['title'] = request.form['title']
        # todo['description'] = request.form['description']
        # todo['done'] = True if 'done' in request.form.keys() else False
      
        # Update fields
        todo.title = request.form['title']
        todo.description = request.form['description']
        todo.done = True if 'done' in request.form.keys() else False
        db.session.commit()  # Save changes

        return redirect(url_for('Todos.index'))
    else:
        return render_template('todos/edit.html', todo=todo, index=index)


@todos.route('/check/<int:index>')
def check(index):
    # todosArr[index]['done'] = not todosArr[index]['done']

    
    todo = Todo.query.get(index)  # or get_or_404(id)
    if todo.done:
        todo.done = False
    else:
        todo.done = True
    db.session.commit()  # Save changes
    return redirect(url_for('Todos.index'))

@todos.route('/delete/<int:index>')
def delete(index):
    #del todosArr[index]
    # return redirect(url_for('Todos.index'))


    Todo.query.filter(Todo.tid == index).delete()
    db.session.commit()
    todos = Todo.query.all()
    
    return redirect(url_for('Todos.index'))

    # return redirect(url_for('Todos.index', todos = todos)) --> output url: http://localhost:5000/todos/?todos=%3CTODO:+sfsdf,+Description:+sdfsdfsdffsdfsdf,+Done:+True%3E&todos=%3CTODO:+vcvcv,+Description:+cvcvcvcv,+Done:+True%3E
    #return render_template('todos/index.html',todosArr = todos)

    # @app.route('/delete/<pid>', methods=['DELETE'])
    # def delete(pid):
    #     Person.query.filter(Person.pid == pid).delete()
        
    #     db.session.commit()
    #     people = Person.query.all()
    #     return render_template('index.html',people = people)
    #     #return redirect(url_for('index'))